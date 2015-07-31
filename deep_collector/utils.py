from cStringIO import StringIO
import logging

from django.db.models import ForeignKey, OneToOneField

from deep_collector.serializers import MultiModelInheritanceSerializer


logger = logging.getLogger(__name__)

class RelatedObjectsCollector(object):
    """
    This class is used to introspect an object, to get every other objects that depend on it, following its
    'relation' fields, i.e. ForeignKey, OneToOneField and ManyToManyField.

    1. We start from given object (of class classA for example), and loop over :

    - Its 'direct' fields, it means the relation fields that are explicitly declared in this django model.
    >>> class classA(models.Model):
    >>>     fkey = models.ForeignKey(classB)
    >>>     o2o = models.OneToOneField(classC)
    >>>     m2m = models.ManyToManyField(classD)

    - Its 'related' fields, so other django model that are related to this object by relation fields.
    >>> class classB(models.Model):
    >>>     fkeyto = models.ForeignKey(classA)
    >>>
    >>> class classC(models.Model):
    >>>     o2oto = models.OneToOneField(classA)
    >>>
    >>> class classD(models.Model):
    >>>     m2mto = models.ManyToManyField(classA)

    2. For every field, we get associated object(s) of objA:

    - If it's a direct field, we get objects by:
    >>> class classA(models.Model):
    >>>     fkey = models.ForeignKey(classB)        # objA.fkey
    >>>     o2o = models.OneToOneField(classC)      # objA.o2o
    >>>     m2m = models.ManyToManyField(classD)    # objA.m2m.all()

    - If it's a related field, we get objects by:
    >>> class classB(models.Model):
    >>>     fkeyto = models.ForeignKey(classA)      # objA.classb_set.all()
    >>>
    >>> class classC(models.Model):
    >>>     o2oto = models.OneToOneField(classA)    # objA.classC (not a manager, because OneToOneField is a unique rel)
    >>>
    >>> class classD(models.Model):
    >>>     m2mto = models.ManyToManyField(classA)  # objA.classd_set.all()

    If we are using related_name attribute, then we access manager with its related_name:
    >>> class classE(models.Model):
    >>>     m2mto = models.ForeignKey(classA, related_name='classE')  # objA.classE.all()

    3. For each associated object, we go back to step 1. and get every field, ...

    ------------------------------------------------------------------------------------------------------------------
    HOWTO use:

    Create a new instance of RelatedObjectsCollector, and launch collector on one object:
    >>> from nested_collector.utils import RelatedObjectsCollector
    >>> from django.contrib.auth.models import User
    >>>
    >>> user = User.objects.all()[0]
    >>> collector = RelatedObjectsCollector()
    >>> collector.collect(user)
    >>> related_objects = collector.get_all_related_objects()

    If you want to save it in a file to be 'django load_data'-like imported, you can use:
    >>> string_buffer = collector.get_json_serialized_objects()

    ------------------------------------------------------------------------------------------------------------------
    PARAMETERS:

    You can customize which model/field is collected.
    By default, every model and field is collected, but you can override some parameters to have custom behaviour:

    - EXCLUDE_MODELS: exclude models (expecting a list of '<app_label>.<module_name>')
    >>> EXCLUDE_MODELS = ['sites.site', 'auth.permission', 'contenttypes.contenttype', 'auth.group']
    Every time we will try to collect an object of this model type, it won't be collected.

    - EXCLUDE_DIRECT_FIELDS: exclude direct fields from specified models
    >>> EXCLUDE_DIRECT_FIELDS = {
            'auth.user': ['groups'],
        }
    On User model, when we will get direct fields, we won't take into account 'groups' field.

    - EXCLUDE_RELATED_FIELDS: Exclude related fields from specified models
    >>> EXCLUDE_RELATED_FIELDS = {
            'auth.user': ['session_set']
        }
    On User model, we don't want to collect sessions that are associated to this user, so we put the exact accessor
    name we have to use to get these session, 'session_set', to exclude it from collecting.

    ------------------------------------------------------------------------------------------------------------------
    MISCELLANEOUS:

    To avoid some recursive collect between 2 objects (if an object has a direct field to another one, it means that
    other object has a related field to this first one), we detect if an object has already been collected before
    trying to collect it.

    We are also avoiding by default to collect objects that have the same type as the root one, to prevent collecting
    too many data. This behaviour can be changed with ALLOWS_SAME_TYPE_AS_ROOT_COLLECT parameter.
    """

    # Models that won't be introspected.
    EXCLUDE_MODELS = []

    # Direct fields that won't be introspected
    EXCLUDE_DIRECT_FIELDS = {}

    # Related fields that won't be introspected
    EXCLUDE_RELATED_FIELDS = {}

    # Allow to recursively collect other objects that have same type as root collected object.
    ALLOWS_SAME_TYPE_AS_ROOT_COLLECT = False

    MAXIMUM_RELATED_INSTANCES = 50
    # We are settings related instances maximum size depending on the model
    MAXIMUM_RELATED_INSTANCES_PER_MODEL = {}

    def clean_by_fields(self, obj, fields, get_field_fn, exclude_list):
        """
        Function used to exclude defined fields from object collect.
        :param parent: the object we are collecting
        :param fields: every field related to this object (direct or reverse one)
        :param get_field_fn: function used to get accessor for each field
        :param exclude_list: model/fields we have defined to be excluded from collect
        :return: fields that are allowed to be collected
        """
        cleaned_list = []
        obj_model = get_model_from_instance(obj)

        for field in fields:
            field_accessor = get_field_fn(field)
            # This field is excluded if:
            # 1/ it's parent model key is in exclude list keys
            # AND
            # 2/ the field has been defined as excluded for this parent model
            is_excluded = obj_model in exclude_list and field_accessor in exclude_list[obj_model]

            if not is_excluded:
                cleaned_list.append(field)

        return cleaned_list

    def get_collected_objects(self):
        return self.collected_objs.values()

    def get_json_serialized_objects(self):
        objects = self.get_collected_objects()

        string_buffer = StringIO()

        serializer = MultiModelInheritanceSerializer()
        serializer.serialize(
            objects,
            stream=string_buffer,
            indent=2
        )
        string_buffer.seek(0)

        return string_buffer

    def _is_already_collected(self, parent, obj):
        new_key = get_key_from_instance(obj)
        parent_key = get_key_from_instance(parent)
        is_already_collected = new_key in self.collected_objs

        if is_already_collected:
            logger.debug('-' * 100)
            logger.debug('Collecting >>> {key} <<< (from {parent_key}) : NOK (already collected)'.format(
                key=new_key, parent_key=parent_key))

        return is_already_collected

    def _is_excluded_model(self, obj):
        obj_model = get_model_from_instance(obj)
        obj_key = get_key_from_instance(obj)
        is_excluded_model = obj_model in self.EXCLUDE_MODELS

        if is_excluded_model:
            logger.debug('-' * 100)
            logger.debug('Not Collecting {key} (excluded model)'.format(key=obj_key))

        return is_excluded_model

    def _is_same_type_as_root(self, obj):
        '''
        Testing if we try to collect an object of the same type as root.
        This is not really a good sign, because it means that we are going to collect a whole new tree, that will
        maybe collect a new tree, that will...
        '''
        if not self.ALLOWS_SAME_TYPE_AS_ROOT_COLLECT:
            obj_model = get_model_from_instance(obj)
            obj_key = get_key_from_instance(obj)
            is_same_type_as_root = obj_model == self.root_obj_model and obj_key != self.root_obj_key

            if is_same_type_as_root:
                logger.debug('*********** WARNING NEW {obj_model} obj : {obj_key} ***************'.format(
                     obj_model=obj_model, obj_key=obj_key
                ))
            return is_same_type_as_root
        else:
            return False

    def is_excluded_from_collect(self, parent, obj):
        is_excluded_from_collect = \
            self._is_already_collected(parent, obj)\
            or self._is_excluded_model(obj)\
            or self._is_same_type_as_root(obj)

        return is_excluded_from_collect

    def add_to_collected_object(self, parent, obj):
        parent_key = get_key_from_instance(parent)
        new_key = get_key_from_instance(obj)

        self.collected_objs[new_key] = obj

        logger.debug('-' * 100)
        logger.debug('Collecting >>> {key} <<< (from {parent_key}) : OK'.format(
            key=new_key, parent_key=parent_key))

        model = get_model_from_instance(obj)
        if model in self.collected_objs_history:
            self.collected_objs_history[model] += 1
        else:
            self.collected_objs_history[model] = 1
        logger.debug(self.collected_objs_history)

    def collect(self, root_obj):
        # Resetting collected_objs if several collects are called.
        self.objects_to_collect = [(None, root_obj)]
        self.collected_objs = {}
        self.collected_objs_history = {}

        self.root_obj_key = get_key_from_instance(root_obj)
        self.root_obj_model = get_model_from_instance(root_obj)

        while self.objects_to_collect:
            parent, obj = self.objects_to_collect.pop()
            children = self._collect(parent, obj)
            self.objects_to_collect += [(obj, child) for child in children]

    def _collect(self, parent, obj):
        if self.is_excluded_from_collect(parent, obj):
            return []
        obj = self.pre_collect(obj)
        self.add_to_collected_object(parent, obj)

        # Local objects are explicit fields on current object model
        local_objs = self.get_local_objs(obj)

        # Related objects are fields defined in other models that can refer to current model
        related_objs = self.get_related_objs(obj)

        self.post_collect(obj)
        return local_objs + related_objs

    def pre_collect(self, obj):
        return obj

    def post_collect(self, obj):
        """
        We want to manage the side-effect of not collecting other items of the same type as root model.
        If for example, you run the collect on a specific user that is linked to a model "A" linked (ForeignKey)
        to ANOTHER user.
        Then the collect won't collect this other user, but the collected model "A" will keep the ForeignKey value of
        a user we are not collecting.
        For now, we set the ForeignKey of ANOTHER user to the root one, to be sure that model "A" will always be linked
        to an existing user (of course, the meaning is changing, but only if this field is not unique.

        Before:
        user1 -> modelA -> user2843

        After collection:
        user1 -> modelA -> user1
        """
        if not self.ALLOWS_SAME_TYPE_AS_ROOT_COLLECT:
            for field in self.get_local_fields(obj):
                if isinstance(field, ForeignKey) and not field.unique:
                    instance = getattr(obj, field.name)
                    root_id = self.root_obj_key.split('.')[2]

                    if get_model_from_instance(instance) == self.root_obj_model and instance.id != root_id:
                        root_django_model = type(instance)
                        setattr(obj, field.name, root_django_model.objects.get(id=root_id))

    def get_local_fields(self, obj):
        # Use the concrete parent class' _meta instead of the object's _meta
        # This is to avoid local_fields problems for proxy models. Refs #17717.
        concrete_model = obj._meta.concrete_model
        return self.clean_by_fields(obj, concrete_model._meta.local_fields,
                          lambda x: x.name, self.EXCLUDE_DIRECT_FIELDS)

    def get_local_m2m_fields(self, obj):
        # Use the concrete parent class' _meta instead of the object's _meta
        # This is to avoid local_fields problems for proxy models. Refs #17717.
        concrete_model = obj._meta.concrete_model
        return self.clean_by_fields(obj, concrete_model._meta.local_many_to_many,
                          lambda x: x.name, self.EXCLUDE_DIRECT_FIELDS)

    def get_maximum_allowed_instances_for_model(self, model):
        if model in self.MAXIMUM_RELATED_INSTANCES_PER_MODEL:
            return self.MAXIMUM_RELATED_INSTANCES_PER_MODEL[model]

        return self.MAXIMUM_RELATED_INSTANCES

    def get_local_objs(self, obj):
        local_objs = []

        for field in self.get_local_fields(obj):
            if isinstance(field, ForeignKey):
                logger.debug('+ local field : ' + field.name)
                try:
                    instance = getattr(obj, field.name)
                    if instance:
                        logger.debug('*' * 80)
                        logger.debug('***** Direct instance for ' + field.name + ' *****')
                        logger.debug('*' * 80)
                        local_objs.append(instance)
                    else:
                        logger.debug('-- No direct instance for ' + field.name)
                except Exception as e:
                    logger.debug('-- No direct instance for ' + field.name)

        for field in self.get_local_m2m_fields(obj):
            logger.debug('+ local m2m field : ' + field.name)
            m2m_manager = getattr(obj, field.name)
            objs_count = m2m_manager.count()

            if not objs_count:
                logger.debug('-- No direct instances for ' + field.name)
            else:
                logger.debug('*' * 80)
                logger.debug('*****  Got {nb} direct instance(s) for {related} *****'.format(
                    nb=objs_count, related=field.name))
                logger.debug('*' * 80)

                if objs_count > self.get_maximum_allowed_instances_for_model(get_model_from_instance(obj)):
                    logger.debug('Too many related objects. Would be irrelevant to introspect...')
                else:
                    local_objs += m2m_manager.all()

        return local_objs

    def get_related_fields(self, obj):
        return self.clean_by_fields(obj, obj._meta.get_all_related_objects(),
                          lambda x: x.get_accessor_name(), self.EXCLUDE_RELATED_FIELDS)

    def get_related_m2m_fields(self, obj):
        return self.clean_by_fields(obj, obj._meta.get_all_related_m2m_objects_with_model(),
                          lambda x:x[0].get_accessor_name(), self.EXCLUDE_RELATED_FIELDS)

    def get_related_objs(self, obj):
        related_objs = []

        for related_field in self.get_related_fields(obj):
            logger.debug('+ related field : ' + related_field.get_accessor_name() + ' (' + related_field.name + ')')
            related_objs += self.query_related_objects(related_field, [obj])

        for related_field, _ in self.get_related_m2m_fields(obj):
            logger.debug('+ related m2m field : ' + related_field.get_accessor_name() + ' (' + related_field.name + ')')
            related_objs += self.query_related_objects(related_field, [obj])

        return related_objs

    def query_related_objects(self, related, objs):
        related_objs = []

        try:
            related_obj_or_manager = getattr(objs[0], related.get_accessor_name())

            if isinstance(related.field, OneToOneField):
                related_objs = [related_obj_or_manager]
            else:
                related_objs = list(related_obj_or_manager.all())
        except Exception as e:
            logger.debug('Exception while getting related objects: %s', str(e))

        if not related_objs:
            logger.debug('-- No related instances for ' + related.name)
        else:
            logger.debug('*' * 80)
            logger.debug('*****  Got {nb} related instance(s) for {related} *****'.format(nb=len(related_objs), related=related.name))
            logger.debug('*' * 80)
            if len(related_objs) > self.get_maximum_allowed_instances_for_model(get_model_from_instance(related_objs[0])):
                logger.debug('Too many related objects. Would be irrelevant to introspect...')
                related_objs = []
        return related_objs


def get_model_from_instance(obj):
    if obj is None:
        return '<root>'

    try:
        meta = obj._meta
    except AttributeError:
        meta = obj.model._meta

    # in django 1.8 _meta.module_name was renamed to _meta.model_name
    model_name = meta.model_name if hasattr(meta, 'model_name') else meta.module_name
    model = meta.app_label + '.' + model_name
    return model


def get_key_from_instance(obj):
    if obj is None:
        return '<root>'
    return get_model_from_instance(obj) + '.' + str(obj.pk)

import factory

from django.conf import settings

try:
    from nested_collector.models import (FKDummyModel, O2ODummyModel, BaseModel, ManyToManyToBaseModel,
        ForeignKeyToBaseModel, OneToOneToBaseModel, ClassLevel1, ClassLevel2, ClassLevel3,
        ManyToManyToBaseModelWithRelatedName, ChildModel)
except ImportError as e:
    if not hasattr(settings, 'NESTED_COLLECTOR_LAUNCH_TESTS'):
        msg = "If you are trying to launch tests for nested_collector app, don't forget to add "
        msg += "'NESTED_COLLECTOR_LAUNCH_TESTS = True' to your test settings. "
        msg += "Models are not created by default because they are test-purpose only, and we don't want them to "
        msg += "pollute production database on syncdb."
        raise Exception(msg)
    else:
        raise(e)


class FKDummyModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "FKDummyModelName#{number}".format(number=str(x)))

    class Meta:
        model = FKDummyModel

class O2ODummyModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "O2ODummyModelName#{number}".format(number=str(x)))

    class Meta:
        model = O2ODummyModel


class BaseModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "BaseModelName#{number}".format(number=str(x)))
    fkey = factory.SubFactory(FKDummyModelFactory)
    o2o = factory.SubFactory(O2ODummyModelFactory)

    class Meta:
        model = BaseModel


class ManyToManyToBaseModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "MaynyToManyToBaseModelName#{number}".format(number=str(x)))

    class Meta:
        model = ManyToManyToBaseModel

    @factory.post_generation
    def base_models(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for base_model in extracted:
                self.m2m.add(base_model)


class ManyToManyToBaseModelWithRelatedNameFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "MaynyToManyToBaseModelName#{number}".format(number=str(x)))

    class Meta:
        model = ManyToManyToBaseModelWithRelatedName

    @factory.post_generation
    def base_models(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for base_model in extracted:
                self.m2m.add(base_model)

class ForeignKeyToBaseModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "ForeignKeyToBseModelName#{number}".format(number=str(x)))
    fkeyto = factory.SubFactory(BaseModelFactory)

    class Meta:
        model = ForeignKeyToBaseModel


class OneToOneToBaseModelFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "OneToOneToBaseModelName#{number}".format(number=str(x)))
    o2oto = factory.SubFactory(BaseModelFactory)

    class Meta:
        model = OneToOneToBaseModel


class ClassLevel1Factory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "ClassLevel1#{number}".format(number=str(x)))

    class Meta:
        model = ClassLevel1


class ClassLevel2Factory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "ClassLevel2#{number}".format(number=str(x)))
    fkey = factory.SubFactory(ClassLevel1Factory)

    class Meta:
        model = ClassLevel2


class ClassLevel3Factory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda x: "ClassLevel3#{number}".format(number=str(x)))
    fkey = factory.SubFactory(ClassLevel2Factory)

    class Meta:
        model = ClassLevel3


class ChildModelFactory(BaseModelFactory):
    child_field = factory.Sequence(lambda x: "ChildField#{number}".format(number=str(x)))

    class Meta:
        model = ChildModel

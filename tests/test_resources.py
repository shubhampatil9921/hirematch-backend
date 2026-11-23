
from app.core.resources import create_resources


class FakeModel:
    def encode(self, sentences, **kwargs):
        return [[0.1, 0.2, 0.3] for _ in (
            sentences if isinstance(sentences, list) else [sentences]
        )]


class FakeESCO:
    def resolve(self, skill):
        return None


def test_resources_share_one_model_instance():
    fake_model = FakeModel()
    fake_esco = FakeESCO()

    resources = create_resources(
        model=fake_model,
        esco_vocabulary=fake_esco,
    )

    service = resources.matching_service

    assert resources.embedding_model is fake_model
    assert service.skill_matcher.model is fake_model
    assert service.title_matcher.model is fake_model


def test_resources_use_supplied_esco_vocabulary():
    fake_esco = FakeESCO()

    resources = create_resources(
        model=FakeModel(),
        esco_vocabulary=fake_esco,
    )

    assert resources.esco_vocabulary is fake_esco
    assert (
        resources.matching_service.skill_matcher.esco_vocabulary
        is fake_esco
    )


def test_resources_create_matching_service():
    resources = create_resources(
        model=FakeModel(),
        esco_vocabulary=FakeESCO(),
    )

    assert resources.matching_service is not None

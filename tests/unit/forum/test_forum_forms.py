"""Tests for flaskbb.forum.forms."""

import pytest
from werkzeug.datastructures import MultiDict

from flaskbb.forum import forms

pytestmark = pytest.mark.usefixtures("post_request_context", "default_settings")


class TestTopicForm:
    def test_valid_inputs_creates_and_saves_topic(self, forum, user):
        data = MultiDict(
            {
                "title": "A brand new topic",
                "content": "Some interesting content",
                "submit": True,
            }
        )
        form = forms.TopicForm(formdata=data, meta={"csrf": False})

        assert form.validate_on_submit()

        topic = form.save(user=user, forum=forum)

        assert topic.title == "A brand new topic"
        assert topic.user_id == user.id
        assert topic.forum_id == forum.id

    @pytest.mark.parametrize(
        "formdata, expected_valid",
        [
            ({"title": "A valid title", "content": "Valid content"}, True),
            (
                {
                    "title": "A valid title",
                    "content": "Valid content",
                    "track_topic": True,
                },
                True,
            ),
            ({"title": "", "content": "Valid content"}, False),
            ({"title": "A valid title", "content": ""}, False),
        ],
    )
    def test_title_and_content_validation(self, formdata, expected_valid):
        data = {"submit": True}
        data.update(formdata)

        form = forms.TopicForm(formdata=MultiDict(data), meta={"csrf": False})

        assert form.validate_on_submit() is expected_valid

    def test_track_topic_calls_user_track_topic(self, forum, user, mocker):
        track_topic_spy = mocker.patch.object(user, "track_topic")

        data = MultiDict(
            {
                "title": "Tracked topic",
                "content": "Content",
                "track_topic": True,
                "submit": True,
            }
        )
        form = forms.TopicForm(formdata=data, meta={"csrf": False})
        assert form.validate_on_submit()

        form.save(user=user, forum=forum)

        track_topic_spy.assert_called_once()

    def test_no_track_topic_calls_user_untrack_topic(self, forum, user, mocker):
        untrack_topic_spy = mocker.patch.object(user, "untrack_topic")

        data = MultiDict(
            {
                "title": "Untracked topic",
                "content": "Content",
                "submit": True,
            }
        )
        form = forms.TopicForm(formdata=data, meta={"csrf": False})
        assert form.validate_on_submit()

        form.save(user=user, forum=forum)

        untrack_topic_spy.assert_called_once()


class TestPostForm:
    def test_valid_input_creates_and_saves_post(self, topic, user):
        data = MultiDict({"content": "A valid reply", "submit": True})
        form = forms.PostForm(formdata=data, meta={"csrf": False})

        assert form.validate_on_submit()

        post = form.save(user=user, topic=topic)

        assert post.content == "A valid reply"
        assert post.user_id == user.id
        assert post.topic_id == topic.id

    def test_empty_content_is_invalid(self):
        data = MultiDict({"content": "", "submit": True})
        form = forms.PostForm(formdata=data, meta={"csrf": False})

        assert not form.validate_on_submit()


class TestReportForm:
    def test_valid_input_saves_report(self, topic, user):
        data = MultiDict({"reason": "This post is spam", "submit": True})
        form = forms.ReportForm(formdata=data, meta={"csrf": False})

        assert form.validate_on_submit()

        report = form.save(user=user, post=topic.first_post)

        assert report.reason == "This post is spam"

    def test_empty_reason_is_invalid(self):
        data = MultiDict({"reason": "", "submit": True})
        form = forms.ReportForm(formdata=data, meta={"csrf": False})

        assert not form.validate_on_submit()

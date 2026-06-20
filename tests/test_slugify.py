from wolai_obsidian_exporter.utils.slugify import slugify_filename, split_wolai_path


def test_slugify_filename_keeps_chinese_and_replaces_unsafe_chars():
    assert slugify_filename("AI视频/教程:01") == "AI视频_教程_01"


def test_slugify_fallback():
    assert slugify_filename("   ") == "untitled"


def test_split_wolai_path():
    assert split_wolai_path("学习笔记 / AI产品经理") == ["学习笔记", "AI产品经理"]

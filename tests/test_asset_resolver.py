from wolai_obsidian_exporter.assets.downloader import extension_from_url_or_name


def test_extension_from_download_query():
    url = "https://example.invalid/download?signature=redacted&download=image.png"
    assert extension_from_url_or_name(url, "") == ".png"


def test_extension_from_name():
    assert extension_from_url_or_name("https://example.invalid/x", "deck.pptx") == ".pptx"

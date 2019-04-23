def test():
    import pride.gui.gui
    window = pride.objects[pride.gui.enable()]
    atlas = window.create(pride.gui.gui.Texture_Atlas)

if __name__ == "__main__":
    test()

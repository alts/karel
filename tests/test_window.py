import karel_robot.window as win


def test_window_import():
    assert win.__doc__, "Should have nonempty module documentation"
    assert True, "Window uses curses, so test it manually"

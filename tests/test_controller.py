from controls.controller import Controller


controller = Controller()


try:

    controller.output(
        {"omega":314}
    )


except NotImplementedError as e:

    print(e)
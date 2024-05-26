import reflex as rx


def index():
    return rx.h1("Hello, Reflex!")


app = rx.App()
app.add_route("/", index)

if __name__ == "__main__":
    app.compile()

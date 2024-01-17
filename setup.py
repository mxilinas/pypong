from cx_Freeze import setup, Executable

include_files = [
    ("data", "data"),
]

setup(
    name="Pong",
    version="1.0",
    description="Pong in python",
    executables=[Executable("pong.py")],
    options={
        "build_exe": {
            "include_files": include_files,
        },
    },
)

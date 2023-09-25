from constants import Constants


def CheckLength(verbose: bool = True) -> None:
    characters = open(Constants.COMMON_CHARACTERS_PATH, "r").readline().strip()
    assert len(characters) == Constants.COMMON_CHARACTERS_COUNT
    if verbose:
        print("CheckLength() succeeds.")

def GetCharacters() -> str:
    characters = open(Constants.COMMON_CHARACTERS_PATH, "r").readline().strip()
    return characters

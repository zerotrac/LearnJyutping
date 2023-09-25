import os
import ToJyutping

from constants import Constants
from tools import GetCharacters


class JyutCharacterKey:
    def __init__(self, character: str) -> None:
        self.character = character

    def __eq__(self, other: "JyutCharacterKey") -> bool:
        return self.character == other.character

    def __hash__(self) -> int:
        return hash(self.character)

    def ToString(self) -> str:
        return self.character

class JyutCharacterValue:
    COLUMNS = 5

    def __init__(self, jyutping: str, learned: int = 0, tested: int = 0, correct: int = 0, incorrect: int = 0) -> None:
        self.jyutping = jyutping
        self.learned = learned
        self.tested = tested
        self.correct = correct
        self.incorrect = incorrect

    def ToString(self) -> str:
        return f"{self.jyutping}\t{self.learned}\t{self.tested}\t{self.correct}\t{self.incorrect}"

    @staticmethod
    def FromString(serialized: str) -> "JyutCharacterValue":
        content = serialized.split("\t")
        assert len(content) == JyutCharacterValue.COLUMNS
        return JyutCharacterValue(content[0], int(content[1]), int(content[2]), int(content[3]), int(content[4]))

class JyutCharacterHelper:
    @staticmethod
    def ToString(key: JyutCharacterKey, value: JyutCharacterValue) -> str:
        return f"{key.ToString()}\t{value.ToString()}"

    @staticmethod
    def FromString(serialized: str) -> (JyutCharacterKey, JyutCharacterValue):
        key, value = serialized.split("\t", maxsplit=1)
        return JyutCharacterKey(key), JyutCharacterValue.FromString(value)

class Tracker:
    TITLE = ["Character", "Jyutping", "Learned", "Tested", "Correct", "Incorrect"]

    def __init__(self) -> None:
        self.jyutping_map = dict()

    def AddRaw(self, character: str, jyutping: str) -> None:
        assert type(character) is str
        assert type(jyutping) is str

        key = JyutCharacterKey(character)
        assert key not in self.jyutping_map
        self.jyutping_map[key] = JyutCharacterValue(jyutping)

    def Add(self, key: JyutCharacterKey, value: JyutCharacterValue) -> None:
        assert type(key) is JyutCharacterKey
        assert type(value) is JyutCharacterValue

        assert key not in self.jyutping_map
        self.jyutping_map[key] = value

    @staticmethod
    def ReadFromFile(target_path: str) -> "Tracker":
        tracker = Tracker()
        with open(target_path, "r") as fin:
            title = fin.readline().strip()
            assert title == "\t".join(Tracker.TITLE)
            assert len(Tracker.TITLE) == JyutCharacterValue.COLUMNS + 1
            for seralized in fin:
                tracker.Add(*JyutCharacterHelper.FromString(seralized.strip()))
        return tracker

    def WriteToFile(self, target_path: str) -> None:
        with open(target_path, "w") as fout:
            fout.write("\t".join(Tracker.TITLE) + "\n")
            for key, value in self.jyutping_map.items():
                fout.write(JyutCharacterHelper.ToString(key, value) + "\n")

    def SampleForLearning(self):
        pass

    def SampleForTesting(self):
        pass

def NewProgressTracking(target_path: str = Constants.PROGRESS_TRACKING_PATH) -> bool:
    if os.path.exists(target_path):
        print(f"File {target_path} already exists.")
        return False

    characters = GetCharacters()
    tracker = Tracker()
    for character in characters:
        jyutping = ToJyutping.get_jyutping_list(character)
        assert len(jyutping) == 1
        assert jyutping[0][1] is not None
        tracker.AddRaw(character, jyutping[0][1])

    tracker.WriteToFile(target_path)
    print(f"A new progress tracking file {target_path} is created.")
    return True


if __name__ == "__main__":
    NewProgressTracking()

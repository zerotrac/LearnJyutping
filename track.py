import os
import ToJyutping

from constants import Constants
from tools import GetCharacters


class JyutCharacter:
    COLUMNS = 6

    def __init__(self, character: str, jyutping: str, learned: int = 0, tested: int = 0, correct: int = 0, incorrect: int = 0) -> None:
        self.character = character
        self.jyutping = jyutping
        self.learned = learned
        self.tested = tested
        self.correct = correct
        self.incorrect = incorrect
    
    def ToString(self) -> str:
        return f"{self.character}\t{self.jyutping}\t{self.learned}\t{self.tested}\t{self.correct}\t{self.incorrect}"
    
    @staticmethod
    def FromString(serialized: str) -> "JyutCharacter":
        content = serialized.split("\t")
        assert len(content) == JyutCharacter.COLUMNS
        return JyutCharacter(content[0], content[1], int(content[2]), int(content[3]), int(content[4]), int(content[5]))
    
    def Duplicate(self) -> "JyutCharacter":
        return JyutCharacter(self.character, self.jyutping, self.learned, self.tested, self.correct, self.incorrect)

class Tracker:
    TITLE = ["Character", "Jyutping", "Learned", "Tested", "Correct", "Incorrect"]

    def __init__(self) -> None:
        self.characters = list()
    
    def Add(self, character: str, jyutping: str) -> None:
        self.characters.append(JyutCharacter(character, jyutping))
    
    def AddFrom(self, character: JyutCharacter) -> None:
        self.characters.append(character.Duplicate())

    @staticmethod
    def ReadFromFile(target_path: str) -> "Tracker":
        tracker = Tracker()
        with open(target_path, "r") as fin:
            title = fin.readline().strip()
            assert title == "\t".join(Tracker.TITLE)
            assert len(Tracker.TITLE) == JyutCharacter.COLUMNS
            for seralized in fin:
                tracker.AddFrom(JyutCharacter.FromString(seralized.strip()))
        return tracker

    def WriteToFile(self, target_path: str) -> None:
        with open(target_path, "w") as fout:
            fout.write("\t".join(Tracker.TITLE) + "\n")
            for character in self.characters:
                fout.write(character.ToString() + "\n")

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
        tracker.Add(character, jyutping[0][1])
    
    tracker.WriteToFile(target_path)
    print(f"A new progress tracking file {target_path} is created.")
    return True


if __name__ == "__main__":
    NewProgressTracking()

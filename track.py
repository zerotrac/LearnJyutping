import os
import random
import sys
import ToJyutping

from constants import Constants
from tools import GetCharacters
from typing import List

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
    
    def GetWeightForLearn(self) -> int:
        return int(1000000 / (1 + self.learned))

    def GetWeightForTest(self) -> int:
        if self.learned == 0:
            return 0

        acc = 1.0 if self.tested == 0 else self.correct / self.tested
        return int(1000000 / (1 + (self.tested ** 0.5)) / (acc + 1e-7))

    def HasLearned(self) -> bool:
        return self.learned > 0

    def DoLearn(self) -> None:
        self.learned += 1

    def DoTest(self, is_correct: bool) -> None:
        self.tested += 1
        if is_correct:
            self.correct += 1
        else:
            self.incorrect += 1

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

    def WriteToFile(self, target_path: str, overwrite: bool = False) -> None:
        if not overwrite and os.path.exists(target_path):
            print(f"File {target_path} already exists.")
            assert False

        with open(target_path, "w") as fout:
            fout.write("\t".join(Tracker.TITLE) + "\n")
            for key, value in self.jyutping_map.items():
                fout.write(JyutCharacterHelper.ToString(key, value) + "\n")

    def SampleForLearning(self, sample_count: int) -> List[JyutCharacterKey]:
        assert sample_count <= len(self.jyutping_map)

        keys, weights = list(), list()
        for key, value in self.jyutping_map.items():
            keys.append(key)
            weights.append(value.GetWeightForLearn())

        samples = set()
        while len(samples) < sample_count:
            need = sample_count - len(samples)
            candidates = random.choices(keys, weights=weights, k=need)
            for candidate in candidates:
                samples.add(candidate)

        return list(samples)

    def OutputForLearning(self, key: JyutCharacterKey, value: JyutCharacterValue) -> None:
        print(f"「{key.character}」（已经学习 {value.learned} 次，测试 {value.correct}/{value.tested} 次）")
        print(f"读音：「\033[32m{value.jyutping}\033[0m」")
        print("=====")

    def DoLearning(self, sample_count: int):
        samples = self.SampleForLearning(sample_count)
        for key in samples:
            value = self.jyutping_map[key]
            self.OutputForLearning(key, value)
            value.DoLearn()
            if input() == "save":
                break
        self.WriteToFile(target_path=Constants.PROGRESS_TRACKING_PATH, overwrite=True)

    def OutputForTesting(self, key: JyutCharacterKey, value: JyutCharacterValue) -> None:
        print(f"「{key.character}」（已经学习 {value.learned} 次，测试 {value.correct}/{value.tested} 次）")

    def ValidateForTesting(self, key: JyutCharacterKey, value: JyutCharacterValue, given: str) -> None:
        if given == value.jyutping:
            print("答案\033[32m正确\033[0m！")
            value.DoTest(True)
        elif given == value.jyutping[:-1]:
            print(f"答案\033[32m正确\033[0m！包含音调是 \033[32m{value.jyutping}\033[0m")
            value.DoTest(True)
        else:
            print(f"答案\033[31m错误\033[0m！应当是 \033[32m{value.jyutping}\033[0m")
            value.DoTest(False)

    def SampleForTesting(self, sample_count: int):
        learned = sum(1 for value in self.jyutping_map.values() if value.HasLearned())
        assert sample_count <= learned

        keys, weights = list(), list()
        for key, value in self.jyutping_map.items():
            if value.HasLearned():
                keys.append(key)
                weights.append(value.GetWeightForTest())

        samples = set()
        while len(samples) < sample_count:
            need = sample_count - len(samples)
            candidates = random.choices(keys, weights=weights, k=need)
            for candidate in candidates:
                samples.add(candidate)

        return list(samples)

    def DoTesting(self, sample_count: int):
        samples = self.SampleForTesting(sample_count)
        for key in samples:
            value = self.jyutping_map[key]
            self.OutputForTesting(key, value)
            given = input("请输入读音：")
            if given == "save":
                break
            self.ValidateForTesting(key, value, given)
        self.WriteToFile(target_path=Constants.PROGRESS_TRACKING_PATH, overwrite=True)

def NewProgressTracking(target_path: str = Constants.PROGRESS_TRACKING_PATH) -> bool:
    characters = GetCharacters()
    tracker = Tracker()
    for character in characters:
        jyutping = ToJyutping.get_jyutping_list(character)
        assert len(jyutping) == 1
        assert jyutping[0][1] is not None
        assert len(jyutping[0][1]) >= 2
        assert 1 <= int(jyutping[0][1][-1]) <= 6
        tracker.AddRaw(character, jyutping[0][1])

    tracker.WriteToFile(target_path)
    print(f"A new progress tracking file {target_path} is created.")
    return True


if __name__ == "__main__":
    op = sys.argv[1]
    if op == "reset":
        if sys.argv[2] == "progress":
            os.system(f"rm {Constants.PROGRESS_TRACKING_PATH}")
            NewProgressTracking(Constants.PROGRESS_TRACKING_PATH)
            print(f"Reset progress tracking file {Constants.PROGRESS_TRACKING_PATH}.")
        else:
            print("No-op.")
    elif op == "learn":
        tracker = Tracker.ReadFromFile(Constants.PROGRESS_TRACKING_PATH)
        count = int(sys.argv[2])
        tracker.DoLearning(count)
    elif op == "test":
        tracker = Tracker.ReadFromFile(Constants.PROGRESS_TRACKING_PATH)
        count = int(sys.argv[2])
        tracker.DoTesting(count)
    else:
        print("No-op.")

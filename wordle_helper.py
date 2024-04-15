from itertools import combinations
from tqdm import tqdm


class WordleHelper():
    def __init__(self, corpus=None, word_length=5):
        if not corpus:
            from nltk.corpus import words
            corpus = [word for word in words.words() if word[0].islower()]
        self.corpus = [x.lower() for x in corpus if len(x) == word_length]
        self.word_length = word_length
        self.letter_frequencies = {chr(k):0 for k in range(97,97+26)}
        self.letter_positions = [{chr(k):0 for k in range(97,97+26)} for _ in range(self.word_length)]
        for word in self.corpus:
            for pos, char in enumerate(word):
                self.letter_frequencies[char] += 1
                self.letter_positions[pos][char] += 1


    def position_score(self, word):
        return sum(self.letter_positions[pos][char] for pos, char in enumerate(word))


    def frequency_score(self, word, exponent=1):
        return sum(self.letter_frequencies[char] ** exponent for char in set(word))


    def __best_k_combinatorial_explorer__(self, starter_chars, starter_words, starter_score, candidates, k, slack=0):
        assert len(candidates) >= k
        if len(starter_words) == self.best_k_starting_words_k:
            f = 0
            if slack > 0:
                f = sum(self.frequency_score(word, 1.5) for word in starter_words)
            self.best_k_starting_words_answer.append((starter_words, starter_score + f))
            return

        for i, (word, score) in enumerate(candidates):
            l_chars = starter_chars.union(set(word))
            l_candidates = [cand for cand in candidates[i+1:] if not (set(cand[0]) & l_chars)]
            if len(l_candidates) >= k-1:
                self.__best_k_combinatorial_explorer__(
                    l_chars,
                    starter_words + [word],
                    starter_score + score,
                    l_candidates,
                    k-1,
                    slack
                )


    def best_k_starting_words(self, k, slack=0):
        self.best_k_starting_words_answer = []
        self.best_k_starting_words_k = k
        ranked_alphabet = [x[0] for x in sorted([(a,b) for a,b in self.letter_frequencies.items()], key=lambda x: x[1], reverse=True)]
        allowed_characters = set(ranked_alphabet[:self.word_length * k + slack])
        candidates = [(word, self.position_score(word)) for word in self.corpus
                          if len(set(word)) == self.word_length and
                             set(word).issubset(allowed_characters)]

        for i, (starter, score) in tqdm(enumerate(candidates), total=len(candidates)):
            starter_chars = set(starter)
            l_candidates = [cand for cand in candidates[i+1:] if not (set(cand[0]) & starter_chars)]
            if len(l_candidates) >= k-1:
                self.__best_k_combinatorial_explorer__(
                    starter_chars,
                    [starter],
                    score,
                    l_candidates,
                    k-1,
                    slack
                )

        if self.best_k_starting_words_answer:
            answer = sorted(self.best_k_starting_words_answer, key=lambda x: x[1], reverse=True)
            del self.best_k_starting_words_answer, self.best_k_starting_words_k
            return [x[0] for x in answer]
        else:
            return self.best_k_starting_words(k, slack + 1)


    def deducer(self, grey: list[str], yellow: list[str], green: dict[int,str]):
        characters = set([chr(k) for k in range(97,97+26)])
        grey = set([x.lower() for x in grey])
        characters -= grey
        answer = [word for word in self.corpus if set(word).issubset(characters)]
        if yellow:
            yellow = set([x.lower() for x in yellow])
            answer = [word for word in answer if yellow.issubset(set(word))]
        if green:
            for k, v in green.items():
                answer = [word for word in answer if word[k]==v.lower()]

        answer = [(word, self.frequency_score(word, 1.5) + self.position_score(word)) for word in answer]
        answer.sort(key = lambda x: x[1], reverse=True)
        return [x[0] for x in answer]

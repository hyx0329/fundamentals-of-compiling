from enum import Enum
import enum


class MatcherState(Enum):
    RUNNING = enum.auto()
    FINISHED = enum.auto()
    ERROR = enum.auto()


class Matcher:
    def __init__(self, dfa_table: (list, tuple), char_list: (list, tuple), start_state: int, terminal_set: set):
        self._dfa_table = dfa_table
        self._character_list = char_list
        self._start_state = start_state
        self._current_state = start_state
        self._terminal_set = terminal_set
        self.state = MatcherState.RUNNING
        self.counter = 0

    def reset(self):
        self.state = MatcherState.RUNNING
        self._current_state = self._start_state
        self.counter = 0

    def terminate(self):
        if self._current_state in self._terminal_set:
            self.state = MatcherState.FINISHED
        else:
            self.state = MatcherState.ERROR

    def consume(self, char):
        """ one char at a time
        :param char: input char, single char
        :return: consumed or not
        """

        assert len(char) == 1
        if self.state != MatcherState.RUNNING:
            return False

        try:
            next_state_idx = self._character_list.index(char)
        except ValueError:
            if self._current_state in self._terminal_set:
                self.state = MatcherState.FINISHED
            else:
                self.state = MatcherState.ERROR
            return False

        current_state = self._current_state
        next_state = self._dfa_table[current_state][next_state_idx]

        if next_state is None:
            if self._current_state in self._terminal_set:
                self.state = MatcherState.FINISHED
            else:
                self.state = MatcherState.ERROR
            return False

        self.counter += 1
        self._current_state = next_state
        return True


class BatchMatcher:
    def __init__(self, matchers: list):
        for matcher in matchers:
            assert isinstance(matcher, Matcher)
        self._matchers = matchers

    def reset(self):
        for matcher in self._matchers:
            matcher.reset()

    def terminate(self):
        for matcher in self._matchers:
            matcher.terminate()

    def consume(self, data: str):
        """
        将字符串转换为记号流

        :param data: 输入字符串
        :return: [[char1, id1], [char2, id2], ... ]
        记号编号根据matcher顺序自动生成
        """

        assert isinstance(data, str), "Invalid Input!"

        self.reset()
        
        symbol_list = list()
        read_pos = 0
        string_length = len(data)

        if string_length == 0:
            symbol_list.append(['', -1])  # -1 表示空串
            return symbol_list

        while read_pos < string_length:
            section_read_position = read_pos
            candidate_stack = list()
            while section_read_position < string_length:
                changed_flag = False
                next_char = data[section_read_position]
                for matcher_idx in range(len(self._matchers)):
                    matcher = self._matchers[matcher_idx]
                    status = matcher.consume(next_char)
                    changed_flag |= status
                    if matcher.counter == section_read_position - read_pos:  # 也就是没接受新字符
                        if matcher.state == MatcherState.FINISHED:
                            candidate_stack.append(matcher_idx)
                section_read_position += 1
                if not changed_flag:
                    break

            self.terminate()

            for matcher_idx in range(len(self._matchers)):
                matcher = self._matchers[matcher_idx]
                if matcher.counter == section_read_position - read_pos:
                    if matcher.state == MatcherState.FINISHED:
                        candidate_stack.append(matcher_idx)

            if len(candidate_stack) == 0:
                current_char = data[read_pos]
                # 用额外的ID表示未知符号
                symbol_list.append([current_char, len(self._matchers)])
                read_pos += 1
                continue

            match_result = candidate_stack.pop()  # 取最长匹配id
            match_length = self._matchers[match_result].counter  # 获取字符串长度
            symbol_list.append(
                [data[read_pos:read_pos+match_length], match_result])  # 记录

            read_pos += match_length
            # 重置状态
            for matcher in self._matchers:
                matcher.reset()

        return symbol_list

class Schulze(object):
    def __init__(self, options=list()):
        self.options = [x for x in options]
        self.ballots = []

    def addBallot(self, ballot):
        for option in ballot.keys():
            if option not in self.options:
                self.options.append(option)
        self.ballots.append(ballot)

    def tally(self):
        ballots = add_candidates(self.ballots, self.options)
        self.defeats = strict_preference(self.options, ballots)
        paths = strongest_paths(self.options, self.defeats)
        return ranking(self.options, paths)

def add_candidates(ballots, options):
    """
    Add missing candidates to each ballot.

      When a given voter does not rank all candidates, then it is
      presumed that this voter strictly prefers all ranked candidates
      to all not ranked candidates and that this voter is indifferent
      between all not ranked candidates.
    """
    result = []
    for ballot in ballots:
        ballot = ballot.copy()
        indifferent = max(ballot.values())+1
        for option in options:
            if option not in ballot:
                ballot[option] = indifferent
        result.append(ballot)
    return result

def strict_preference(options, ballots):
    """
    Returns a dictionary of strict preferences between options
    d[a][b] is the number of voters who strictly prefer option a
    over option b.
    """
    d = dict((x, dict((y, 0) for y in options))
             for x in options)
    for ballot in ballots:
        for opt1 in options:
            for opt2 in options:
                if ballot[opt1] < ballot[opt2]:
                    d[opt1][opt2] += 1
    return d

def strongest_paths(options, defeats):
    """
    Return a dictionary of the strongest paths between options.
    p[a][b] is the strength of the strongest path from a to b.
    """
    # Floyd-Warshall algorithm
    p = dict((x, {}) for x in options)
    for opt1 in options:
        for opt2 in options:
            if opt1 != opt2:
                if defeats[opt1][opt2] > defeats[opt2][opt1]:
                    p[opt1][opt2] = defeats[opt1][opt2]
                else:
                    p[opt1][opt2] = 0
    for opt1 in options:
        for opt2 in options:
            if opt1 != opt2:
                for opt3 in options:
                    if ((opt1 != opt3) and (opt2 != opt3)):
                        p[opt2][opt3] = max(p[opt2][opt3],
                                            min(p[opt2][opt1], p[opt1][opt3]))
    return p

def winners(options, paths):
    """
    Return the list of winners among the options, given strongest paths.
    """
    w = [x for x in options]
    for opt1 in options:
        for opt2 in options:
            if opt1 != opt2:
                if ((paths[opt2][opt1] > paths[opt1][opt2]) and
                    opt1 in w):
                    w.remove(opt1)
    return w

def ranking(options, paths):
    options = [x for x in options]
    r = []
    while len(options) > 0:
        w = winners(options, paths)
        r.append(w)
        for opt in w:
            options.remove(opt)
    return r

if __name__ == '__main__':
    def vote(s, number, array):
        for i in range(0, number):
            s.addBallot(dict(zip(array, range(1, len(array)))))
    # Wikipedia Example 1
    s = Schulze()
    vote(s, 5, ['A', 'C', 'B', 'E', 'D'])
    vote(s, 5, ['A', 'D', 'E', 'C', 'B'])
    vote(s, 8, ['B', 'E', 'D', 'A', 'C'])
    vote(s, 3, ['C', 'A', 'B', 'E', 'D'])
    vote(s, 7, ['C', 'A', 'E', 'B', 'D'])
    vote(s, 2, ['C', 'B', 'A', 'D', 'E'])
    vote(s, 7, ['D', 'C', 'E', 'B', 'A'])
    vote(s, 8, ['E', 'B', 'A', 'D', 'C'])
    ballots = add_candidates(s.ballots, s.options)
    defeats = strict_preference(s.options, ballots)
    assert defeats['A']['B'] == 20
    assert defeats['A']['C'] == 26
    assert defeats['A']['D'] == 30
    assert defeats['A']['E'] == 22
    assert defeats['B']['A'] == 25
    assert defeats['B']['C'] == 16
    assert defeats['B']['D'] == 33
    assert defeats['B']['E'] == 18
    assert defeats['C']['A'] == 19
    assert defeats['C']['B'] == 29
    assert defeats['C']['D'] == 17
    assert defeats['C']['E'] == 24
    assert defeats['D']['A'] == 15
    assert defeats['D']['B'] == 12
    assert defeats['D']['C'] == 28
    assert defeats['D']['E'] == 14
    assert defeats['E']['A'] == 23
    assert defeats['E']['B'] == 27
    assert defeats['E']['C'] == 21
    assert defeats['E']['D'] == 31
    paths = strongest_paths(s.options, defeats)
    assert paths['A']['B'] == 28
    assert paths['A']['C'] == 28
    assert paths['A']['D'] == 30
    assert paths['A']['E'] == 24
    assert paths['B']['A'] == 25
    assert paths['B']['C'] == 28
    assert paths['B']['D'] == 33
    assert paths['B']['E'] == 24
    assert paths['C']['A'] == 25
    assert paths['C']['B'] == 29
    assert paths['C']['D'] == 29
    assert paths['C']['E'] == 24
    assert paths['D']['A'] == 25
    assert paths['D']['B'] == 28
    assert paths['D']['C'] == 28
    assert paths['D']['E'] == 24
    assert paths['E']['A'] == 25
    assert paths['E']['B'] == 28
    assert paths['E']['C'] == 28
    assert paths['E']['D'] == 31
    assert s.tally() == [['E'], ['A'], ['C'], ['B'], ['D']]
    # Wikipedia Example 4 / Schulze Example 1
    s = Schulze()
    vote(s, 3, ['A', 'B', 'C', 'D'])
    vote(s, 2, ['D', 'A', 'B', 'C'])
    vote(s, 2, ['D', 'B', 'C', 'A'])
    vote(s, 2, ['C', 'B', 'D', 'A'])
    assert s.tally() == [['B', 'D'], ['A', 'C']]
    # Wikipedia Example 5
    s = Schulze()
    vote(s, 42, ['Memphis', 'Nashville', 'Chattanooga', 'Knoxville'])
    vote(s, 26, ['Nashville', 'Chattanooga', 'Knoxville', 'Memphis'])
    vote(s, 15, ['Chattanooga', 'Knoxville', 'Nashville', 'Memphis'])
    vote(s, 42, ['Knoxville', 'Chattanooga', 'Nashville', 'Memphis'])
    assert s.tally() == [['Nashville'], ['Chattanooga'], ['Knoxville'], ['Memphis']]
    # Late additions
    s = Schulze()
    s.addBallot({'Major': 1, 'Colonel': 2})
    s.addBallot({'Major': 2, 'Colonel': 1})
    s.addBallot({'Major': 1, 'Colonel': 3, 'Captain': 2})
    assert s.tally() == [['Major'], ['Colonel'], ['Captain']]
    print "All tests successful."

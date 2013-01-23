class Database(object):
    def __init__(self):
        self.dragon_bear = []


class Query(object):
    def __init__(self):
        self.db = Database().dragon_bear
        self.log = []

    def do(self, action, addToLog=False, printOutput=True):
        """Given a query action, parse and do the action.
        If addToLog, then also add the rollback action to the log.
        If printOutput, then also print to the console.

        Commands recognized:
        SET [name] [value]
        GET [name]
        UNSET [name]
        NUMEQUALTO [value]
        END
        BEGIN
        ROLLBACK
        COMMIT
        PRINTLOG
        """
        if self.log and printOutput:
            addToLog = True
        command, arg1, arg2 = self.parse(action)
        if command == 'SET':
            self.SET(arg1, arg2, addToLog)
        elif command == 'GET':
            if printOutput:
                print self.GET(arg1)[0]
        elif command == 'UNSET':
            self.UNSET(arg1, addToLog)
        elif command == 'NUMEQUALTO':
            if printOutput:
                print self.NUMEQUALTO(arg1)
        elif command == 'END':
            self.END()
        elif command == 'BEGIN':
            self.BEGIN()
        elif command == 'ROLLBACK':
            self.ROLLBACK()
        elif command == 'COMMIT':
            self.COMMIT()
        elif command == 'PRINTLOG':
            self.PRINTLOG()
        else:
            print 'Python-Dragon-Bear tilts its head in confusion.'

    def parse(self, action):
        """Given an action str, return a length 3 argument list."""
        parts = action.split()
        while len(parts) < 3:
            parts += [0]
        return parts

    def GET(self, key):
        result = 'NULL'
        index = 0
        for i, (k, v) in enumerate(self.db):
            if key == k:
                result = v
                index = i
        return [result, index]

    def SET(self, key, val, addToLog):
        v, i = self.GET(key)
        if v == 'NULL':
            i = self._SET_where(val, self.db)
            rollback = 'UNSET {0}'.format(key)
            self.db = self.db[:i] + [[key, val]] + self.db[i:]
        else:
            rollback = 'SET {0} {1}'.format(key, v)
            self.db[i] = [key, val]
        if addToLog:
            self.log.append(rollback)

    def _SET_where(self, val, data, counter=0):
        """Given a value and a sorted list of [key,value] pairs, recursively
        return the int list index in which the value should be sorted into.
        """
        l = len(data)
        if l == 1:
            if val < data[0][1]:
                return counter
            return counter+1
        elif l == 0:
            return counter
        if val < data[l/2][1]:
            return self._SET_where(val, data[:l/2], counter)
        else:
            return self._SET_where(val, data[l/2:], counter+l/2)

    def UNSET(self, key, addToLog):
        v, i = self.GET(key)
        if v != 'NULL':
            self.db.remove([key,v])
        if addToLog:
            self.log.append('SET {0} {1}'.format(key, v))

    def NUMEQUALTO(self, val):
        count = 0
        for _, v in self.db:
            if v >= val:
                if v == val:
                    count += 1
                    continue
                break
        return count

    def END(self):
        while self.log:
            rollback = self.log.pop()
            if rollback == 'BEGIN':
                continue
            self.do(rollback, addToLog=False, printOutput=False)
        raise EOFError

    def BEGIN(self):
        self.log.append('BEGIN')

    def ROLLBACK(self):
        if not self.log:
            print 'INVALID ROLLBACK'
            return
        while self.log:
            rollback = self.log.pop()
            if rollback == 'BEGIN':
                break
            self.do(rollback, addToLog=False, printOutput=False)

    def COMMIT(self):
        self.log = []

    def PRINTLOG(self):
        print self.log


if __name__ == '__main__':
    query = Query()
    print 'Python-Dragon-Bear awakens. What do you ask of it?'
    while True:
        try:
            q = raw_input("\xE2\x9A\xA1 ")
            query.do(q)
        except EOFError:
            print 'Python-Dragon-Bear says: "Goodbye now, friend."'
            break


class BaseSerializableObject:
    def __init__(self, *args, **kwargs):
        self._obj = dict()
        self._can_set = True

    def __getattr__(self, item):
        return self._obj[item]

    def __getitem__(self, item):
        return self._obj[item]

    def __setitem__(self, key, value):
        if key in self._obj:
            self._obj[key] = value
        else:
            raise KeyError

    def __iter__(self):
        for k, v in self._obj.items():
            if type(v) in [bool, type(None), int, float, str, dict]:
                yield k, v
            elif type(v) in [list, tuple]:
                arr = []
                for el in v:
                    if type(el) in [bool, type(None), int, float, str, dict]:
                        arr.append(el)
                    else:
                        arr.append(dict(el))
                yield k, arr
            else:
                yield k, dict(v)

    def __str__(self):
        return str(self._obj)


class Question(BaseSerializableObject):
    def __init__(self, question_obj: dict=dict(), **kwargs):
        super(Question, self).__init__(**kwargs)
        self._obj["points"] = 1
        self._obj["answer"] = None
        self._obj["answer_variants"] = list()
        self._obj["img"] = None  # url
        self._obj["text"] = None
        self._obj["result"] = None
        question_obj.update(kwargs)

        for key, value in question_obj.items():
            if key in self._obj:
                self._obj[key] = value


class Test(BaseSerializableObject):
    def __init__(self, test_obj: dict=dict(), **kwargs):
        super(Test, self).__init__(**kwargs)
        self._obj["name"] = None
        self._obj["price"] = 0.0
        self._obj["description"] = ""
        self._obj["is_exam"] = False
        self._obj["current_question"] = None
        self._obj["questions"] = list()
        self._obj["is_available"] = True
        test_obj.update(kwargs)

        for key, value in test_obj.items():
            if key == "questions":
                for q in test_obj["questions"]:
                    self._obj["questions"].append(Question(q))
            elif key in self._obj:
                self._obj[key] = value


class Package(BaseSerializableObject):
    def __init__(self, package_obj: dict=dict(), **kwargs):
        super(Package, self).__init__(**kwargs)
        self._obj["name"] = None
        self._obj["description"] = ""
        self._obj["short_description"] = ""
        self._obj["price"] = 0.0
        self._obj["tests"] = list()
        package_obj.update(kwargs)

        for key, value in package_obj.items():
            if key == "tests":
                for t in package_obj["tests"]:
                    self._obj["tests"].append(Test(t))
            elif key in self._obj:
                self._obj[key] = value


if __name__ == "__main__":
    from pprint import pprint

    # x = {"name": "pkg_1", "tests": [{"name": "test_1", "questions": [{}, {}]}]}
    # p = Package(x, price=100.0)
    # pprint(dict(p))
    t = Test({"name": "xxx"})
    pprint(dict(t))

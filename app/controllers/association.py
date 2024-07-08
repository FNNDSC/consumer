# imports
from app.models.association import Association, AssociationList, PACSqueryCore
from app.config import rules


def add_rule(rule: Association) -> dict:
    rules.rules.append(rule)
    return {"message" : "New association added successfully"}

def get_rules() -> AssociationList:
    return rules

def get_analyses(query: PACSqueryCore) -> list[str]:
    list_analyses = []
    for association in rules.rules:
        is_valid = True
        for item in query.__dict__:
            if association["tags"][item]:
                if association["tags"][item] == query.__dict__[item]:
                    continue
                else:
                    is_valid = False
                    break
        if is_valid:
            list_analyses.append(association["analysis_name"])

    print(list_analyses)
    return list_analyses
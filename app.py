from flask import Flask
from flask import request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def psych():
    return "lets get crackin"

@app.route("/getFileStructure", methods = ['POST'])
def getFileStructure():
    if not request.is_json:
        return "Sorry, no Json Request"
    content = request.get_json()
    data = json.dumps(content)
    hierarchy = json.loads(data)

    graph = []

    for folder in hierarchy:
        if(folder['parent'])== 1:
            relation = str(folder['parent'])+"(root)" + " --> " + str(folder['id']) + "(" + str(folder['name']) + ")"
            graph.append(relation)
        else:
            relation = str(folder['parent']) + " --> " + str(folder['id'])+"("+str(folder['name'])+")"
            graph.append(relation)

    seperator = "\n"
    graphLinks = seperator.join(graph)
    graphLinks = "graph TD\n" + graphLinks
    print(graphLinks)

    return graphLinks


@app.route('/getHierarchy/<parentId>', methods = ['POST'])
def getChildren(parentId):

    parentId = int(parentId)
    if not request.is_json:
        return "Sorry, no Json Request"

    content = request.get_json()
    data = json.dumps(content)
    list = json.loads(data)

    #ASSUMPTION: this is a top down tree hierarchy where each node can only have one parent

    children = []
    childrenObjects = []
    unresolvedObjects =[]
    notChildren = []
    ancestors = []
    unresolved = []

    def addChildrenObjects():
        print(str(len(unresolvedObjects)))
        for object in unresolvedObjects:
            childrenObjects.append(object)

    def assign(unresolved,relation):
        for previous in unresolved:
            relation.append(previous)
        unresolved.clear()

    #TODO: put in check if parentID doesn't exist, i e self is empty

    def resolveNode(folder):
        #print(str(folder['id']))
        if folder['parent'] == 1:
            #print(str(folder['id']) + " has parent root, which is not our parentId")
            notChildren.append(folder['id'])
            if len(unresolved) != 0:
                assign(unresolved, notChildren)
                unresolvedObjects.clear()
                #print("added unresolved to NOT children")
            return
        if folder['id'] == parentId:
            #print(str(folder['id'])+ "is self")
            if(folder['id'] not in notChildren):
                notChildren.append(folder['id'])
            if (folder['id'] not in ancestors):
                ancestors.append(folder['parent'])
            if len(unresolved) != 0:
                assign(unresolved, children)
                addChildrenObjects()
                unresolvedObjects.clear()
                #print("added unresolved to children")
            return
        if folder['parent'] == parentId:
            #print(str(folder['id']) + "is direct child")
            if (folder['id'] not in children):
                children.append(folder['id'])
                childrenObjects.append(folder)
            if len(unresolved) != 0:
                assign(unresolved, children)
                addChildrenObjects()
                unresolvedObjects.clear()
                #print("added unresolved to children")
            return
        if folder['id'] in ancestors:
            #print(str(folder['id']) + "is ancestor")
            if len(unresolved) != 0:
                assign(unresolved, ancestors)
                unresolvedObjects.clear()
                #print("added unresolved to ancestors")
            if folder['parent'] not in ancestors:
                if (folder['id'] not in ancestors):
                    ancestors.append(folder['parent'])
                return
            return
        if folder['parent'] in ancestors:
            #print(str(folder['id']) + "is either ancestor or diff branch")
            if (folder['id'] not in notChildren):
                notChildren.append(folder['id'])
            if len(unresolved) != 0:
                assign(unresolved, notChildren)
                unresolvedObjects.clear()
                #print("added unresolved to NOT children")
            return
        if folder['parent'] in children:
            #print(str(folder['id']) + "is indirect child")
            if (folder['id'] not in children):
                children.append(folder['id'])
                childrenObjects.append(folder)
            if len(unresolved) != 0:
                #if the parent is an indirect child then so are unresolved
                assign(unresolved, children)
                addChildrenObjects()
                unresolvedObjects.clear()
                #print("added unresolved to children")
            return
        if folder['parent'] in notChildren:
            #print(str(folder['id']) + "has parent from different branch or ancestor")
            if (folder['id'] not in notChildren):
                notChildren.append(folder['id'])
            if len(unresolved) != 0:
                assign(unresolved, notChildren)
                unresolvedObjects.clear()
                #print("added unresolved to NOT children")
            return
        if (len(children),len(notChildren),len(ancestors)) == len(list):
            #print("all elements are sorted")
            return
        #print(str(folder['id']) + " is unresolved")
        unresolved.append(folder['id'])
        unresolvedObjects.append(folder)
        currentParent = folder['parent']

        for folder in list:
            if folder['id'] == currentParent:
                print("travel up tree to find " + str(currentParent))
                resolveNode(folder);

    if parentId == 1:
        return data;
    else:
        for folder in list:
            resolveNode(folder);

    childrenJson = json.dumps(childrenObjects)
    return childrenJson

if __name__ == "__main__":
    app.run()(debug=True)

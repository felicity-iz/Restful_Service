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

    def addChildrenObjects(unresolvedObjects):
        for previous in unresolvedObjects:
            childrenObjects.append(previous)
        unresolvedObjects.clear()

    def assign(unresolved,relation):
        for previous in unresolved:
            relation.append(previous)

        unresolved.clear()

    def resolveNode(folder):
        if folder['parent'] == 1:
            #print(str(folder['id']) + " has parent root, which is not our parentId")
            notChildren.append(folder['id'])
            return
        if folder['id'] == parentId:
            #print(str(folder['id'])+ "is self")
            notChildren.append(folder['id'])
            ancestors.append(folder['parent'])
            if len(unresolved) != 0:
                assign(unresolved, children)
            return
        if folder['parent'] == parentId:
            #print(str(folder['id']) + "is direct child")
            children.append(folder['id'])
            childrenObjects.append(folder)
            if len(unresolved) != 0:
                assign(unresolved, children)
                addChildrenObjects(unresolvedObjects)
            return
        if folder['id'] in ancestors:
            #print(str(folder['id']) + "is ancestor")
            if len(unresolved) != 0:
                assign(unresolved, ancestors)
                unresolvedObjects.clear()
            if folder['parent'] not in ancestors:
                ancestors.append(folder['parent'])
                return
            return
        if folder['parent'] in ancestors:
            #print(str(folder['id']) + "is either ancestor or diff branch")
            notChildren.append(folder['id'])
            if len(unresolved) != 0:
                assign(unresolved, notChildren)
                unresolvedObjects.clear()
            return
        if folder['parent'] in children:
            #print(str(folder['id']) + "is indirect child")
            children.append(folder['id'])
            childrenObjects.append(folder)
            if len(unresolved) != 0:
                #if the parent is and indirect child then so are unresolved
                assign(unresolved, notChildren)
                addChildrenObjects(unresolvedObjects)
            return
        if folder['parent'] in notChildren:
            #print(str(folder['id']) + "has parent from different branch")
            notChildren.append(folder['id'])
            return
        #print(str(folder['id']) + "is unresolved")
        unresolved.append(folder['id'])
        unresolvedObjects.append(folder)
        currentParent = folder['parent']

        for folder in list:
            if folder['id'] == currentParent:
                #travels up the tree until it resolves
                resolveNode(folder['parent']);

    if parentId == 1:
        return data;
    else:
        for folder in list:
            resolveNode(folder);

    childrenJson = json.dumps(childrenObjects)
    return childrenJson

if __name__ == "__main__":
    app.run()(debug=True)

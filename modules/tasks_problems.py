from modules.parsableText import ParsableText
from abc import ABCMeta,abstractmethod
from modules.tasks_code_boxes import InputBox, MultilineBox, TextBox

#Basic problem. Should not be instanced
class BasicProblem:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def getType(self):
        return None
    @abstractmethod
    def showInput(self):
        return None
    @abstractmethod
    def evalResults(self,formInput):
        return None
    
    def getId(self):
        return self.id
    def getTask(self):
        return self.task
    def getName(self):
        return self.name
    def getHeader(self):
        return self.header
    
    def __init__(self,task,problemId,content):
        if "name" not in content or not isinstance(content['name'], basestring):
            raise Exception("Invalid name for problem "+id)
        if "header" not in content or not isinstance(content['header'], basestring):
            raise Exception("Invalid header for problem "+id)
        
        self.id = problemId
        self.task = task
        self.name = content['name']
        self.header = ParsableText(content['header'],"HTML" if "headerIsHTML" in content and content["headerIsHTML"] else "rst")

#Basic problem with code input. Do all the job with the backend
class BasicCodeProblem(BasicProblem):
    def __init__(self,task,problemId,content):
        BasicProblem.__init__(self, task, id, content)
        if task.getEnvironment() == None:
            raise Exception("Environment undefined, but there is a problem with type=code or type=code-single-line")
        
    def showInput(self):
        return "" #TODO
    
    def evalResults(self,formInput):
        return "" #TODO 
    
    def createBox(self,boxId,boxContent):
        if not boxId.isalnum() and not boxId == "":
            raise Exception("Invalid box id "+boxId)
        if "type" not in boxContent:
            raise Exception("Box "+boxId+" does not have a type")
        if boxContent["type"] == "multiline":
            return MultilineBox(self,boxId,boxContent)
        elif boxContent["type"] == "text":
            return TextBox(self,boxId,boxContent)
        elif boxContent["type"] in ["input-text","input-mail","input-decimal","input-integer"]:
            return InputBox(self,boxId,boxContent)
        else:
            raise Exception("Unknow box type "+boxContent["type"]+ "for box id "+boxId)
        

#Code problem with a single line of input
class CodeSingleLineProblem(BasicCodeProblem):
    def __init__(self,task,problemId,content):
        BasicCodeProblem.__init__(self,task,problemId,content)
        self.boxes = {"":self.createBox("", {"type":"input-text"})}
    def getType(self):
        return "code-single-line"
    
#Code problem 
class CodeProblem(BasicCodeProblem):
    def __init__(self,task,problemId,content):
        BasicCodeProblem.__init__(self,task,problemId,content)
        if "boxes" in content:
            self.boxes = {}
            for boxId, boxContent in content['boxes'].iteritems():
                self.boxes[boxId] = self.createBox(boxId, boxContent)
        else:
            self.boxes = {"":self.createBox("", {"type":"multiline"})}
    def getType(self):
        return "code"

#Multiple choice problems
class MultipleChoiceProblem(BasicProblem):
    def __init__(self,task,problemId,content):
        BasicProblem.__init__(self,task,problemId,content)
        self.multiple = "multiple" in content and content["multiple"]
        if "choices" not in content or not isinstance(content['choices'], list):
            raise Exception("Multiple choice problem "+ problemId +" does not have choices or choices are not an array")
        goodChoices=[]
        badChoices=[]
        for choice in content["choices"]:
            data={}
            if "text" not in choice:
                raise Exception("A choice in "+problemId+" does not have text")
            data['text'] = ParsableText(choice['text'], 'HTML' if "textIsHTML" in choice and choice['textIsHTML'] else 'rst')
            if "valid" in choice and choice['valid']:
                goodChoices.append(data)
            else:
                badChoices.append(data)
        
        if len(goodChoices) == 0:
            raise Exception("Problem "+problemId+" does not have any valid answer")
        
        self.limit = 0
        if "limit" in content and isinstance(content['limit'],(int,long)) and content['limit'] >= 0 and content['limit'] >= len(goodChoices):
            self.limit = content['limit']
        elif "limit" in content:
            raise Exception("Invalid limit in problem "+problemId)
        
        self.choices = goodChoices+badChoices
    def getType(self):
        return "multiple-choice"
    def showInput(self):
        return None #TODO
    def evalResults(self,formInput):
        return None #TODO

#Creates a new instance of the right class for a given problem.
def CreateTaskProblem(task,problemId,problemContent):
    #Basic checks
    if not problemId.isalnum():
        raise Exception("Invalid problem id: "+problemId)
    if "type" not in problemContent or problemContent['type'] not in ["code","code-single-line","multiple-choice"]:
        raise Exception("Invalid type for problem "+problemId)
    
    #If there is code to send, a VM name must be present
    if problemContent['type'] in ["code","code-single-line"] and task.getEnvironment() == None:
        raise Exception("Environment undefined, but there is a problem with type=code")
    
    if problemContent['type'] == "code":
        return CodeProblem(task,problemId,problemContent)
    elif problemContent['type'] == "code-single-line":
        return CodeSingleLineProblem(task,problemId,problemContent)
    elif problemContent['type'] == "multiple-choice":
        return MultipleChoiceProblem(task,problemId,problemContent)
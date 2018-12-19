from abc import ABC, abstractmethod


class Requirement(ABC):
    '''
    Requirement that must be met in order to execute the process.
    '''

    def __init__(self, req_class):
        '''
        :param req_class: requirement class
        :type req_class: STRING
        '''
        # class is protected keyword
        self.req_class = req_class

    @abstractmethod
    def get_dict(self):
        return {"class": self.req_class}


class InlineJavascriptReq(Requirement):
    """
    Indicates that the workflow platform must support inline Javascript expressions.
    If this requirement is not present, the workflow platform must not perform expression interpolatation.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#InlineJavascriptRequirement
    """

    def __init__(self, expression_lib=None):
        '''
        :param expression_lib: List of Strings
        :type expression_lib: STRING | list[STRING]
        '''
        Requirement.__init__(self, 'InlineJavascriptRequirement')
        self.expressionLib = expression_lib

    def get_dict(self):
        base = Requirement.get_dict(self)
        if self.expressionLib:
            base["expressionLib"] = self.expressionLib
        return base


class SchemaDefRequirement(Requirement):
    """
    This field consists of an array of type definitions which must be used when interpreting the inputs and
    outputs fields. When a type field contain a IRI, the implementation must check if the type is defined
    in schemaDefs and use that definition. If the type is not found in schemaDefs, it is an error.
    The entries in schemaDefs must be processed in the order listed such that later schema definitions
    may refer to earlier schema definitions.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#SchemaDefRequirement
    """

    def __init__(self, types):
        """
        :param types: The list of type definitions.
        :type types: list[InputRecordSchema | InputEnumSchema | InputArraySchema]
        """
        Requirement.__init__(self, "SchemaDefRequirement")
        self.types = types

    def get_dict(self):
        base = Requirement.get_dict(self)
        base['types'] = [t.get_dict() for t in self.types]

    # class InputRecordSchema(object):
    #     """
    #     Documentation: https://www.commonwl.org/v1.0/Workflow.html#InputRecordSchema
    #     """
    #     def __init__(self, label=None, name=None):
    #         """
    #         :param fields: Defines the fields of the record.
    #         :type fields: array<InputRecordField>
    #         :param label: A short, human-readable label of this object.
    #         :param name: NF (Name of the InputRecord)
    #         """
    #         self.fields = []
    #         self.label = label
    #         self.name = name
    #
    #     def get_dict(self):
    #         schema = {"type": "record"}
    #         if self.fields:
    #             schema["fields"] = {f.name: f.get_dict() for f in self.fields}
    #         if self.label:
    #             schema["label"] = self.label
    #         if self.name:
    #             schema["name"] = self.name
    #         return schema


class SoftwareRequirement(Requirement):
    """
    A list of software packages that should be configured in the environment of the defined process.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#SoftwareRequirement
    """
    def __init__(self):
        Requirement.__init__(self, "SoftwareRequirement")
        self.packages = []      # list[SoftwarePackage]

    def get_dict(self):
        base = Requirement.get_dict(self)
        base["packages"] = [p.get_dict() for p in self.packages]

    class SoftwarePackage(object):
        """
        Documentation: https://www.commonwl.org/v1.0/Workflow.html#SoftwarePackage
        """
        def __init__(self, package, version=None, specs=None):
            """
            :param package: The name of the software to be made available. If the name is common, inconsistent,
                            or otherwise ambiguous it should be combined with one or more identifiers in the specs field
            :param version: The (optional) versions of the software that are known to be compatible.
            :param specs: One or more IRIs identifying resources for installing or enabling the software in 'package'
            """
            self.package = package
            self.version = version
            self.specs = version

        def get_dict(self):
            base = {"package": self.package}
            if self.version:
                base["version"] = self.version
            if self.specs:
                base["specs"] = self.specs


class InitialWorkDirRequirement(Requirement):
    """
    Define a list of files and subdirectories that must be created by the workflow
    platform in the designated output directory prior to executing the command line tool.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#InitialWorkDirRequirement
    """
    def __init__(self, listing):
        """
        :param listing: The list of files or subdirectories that must be placed in the
                        designated output directory prior to executing the command line tool.
        :type listing: array<File | Directory | Dirent | string | Expression> | string | Expression
        """
        Requirement.__init__(self, "InitialWorkDirRequirement")
        self.listing = listing

    def get_dict(self):
        base = Requirement.get_dict(self)

        if isinstance(self.listing, str):
            base["listing"] = self.listing
        elif isinstance(self.listing, list):
            if len(self.listing) == 1:
                raise Exception("InitialWorkDirRequirement.listing must have at least one element")
            base["listing"] = [r if isinstance(r, str) else r.get_dict() for r in self.listing]
        else:
            raise Exception("Couldn't recognise type of '{list_type}', expected: array<File | Directory | Dirent | "
                            "string| Expression> | string | Expression".format(list_type=type(self.listing)))

        return base

    class Dirent(object):
        """
        Define a file or subdirectory that must be placed in the designated output directory
        prior to executing the command line tool. May be the result of executing an expression,
        such as building a configuration file from a template.

        Documentation: https://www.commonwl.org/v1.0/Workflow.html#Dirent
        """
        def __init__(self, entry, entryname=None, writable=None):
            self.entry = entry
            self.entryname = entryname
            self.writable = writable

        def get_dict(self):
            return {k: v for k, v in vars(self).items() if v is not None}


class SubworkflowFeatureRequirement(Requirement):
    """
    Indicates that the workflow platform must support nested workflows in the run field of WorkflowStep.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#SubworkflowFeatureRequirement
    """

    def __init__(self):
        Requirement.__init__(self, 'SubworkflowFeatureRequirement')

    def get_dict(self):
        return Requirement.get_dict(self)


class ScatterFeatureRequirement(Requirement):
    """
    Indicates that the workflow platform must support the scatter and scatterMethod fields of WorkflowStep.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#ScatterFeatureRequirement
    """

    def __init__(self):
        Requirement.__init__(self, 'ScatterFeatureRequirement')

    def get_dict(self):
        return Requirement.get_dict(self)


class MultipleInputFeatureRequirement(Requirement):
    """
    Indicates that the workflow platform must support multiple
    inbound data links listed in the source field of WorkflowStepInput.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#MultipleInputFeatureRequirement
    """

    def __init__(self):
        Requirement.__init__(self, 'MultipleInputFeatureRequirement')

    def get_dict(self):
        return Requirement.get_dict(self)


class StepInputExpressionRequirement(Requirement):
    """
    Indicate that the workflow platform must support the valueFrom field of WorkflowStepInput.

    Documentation: https://www.commonwl.org/v1.0/Workflow.html#StepInputExpressionRequirement
    """

    def __init__(self):
        Requirement.__init__(self, 'StepInputExpressionRequirement')

    def get_dict(self):
        return Requirement.get_dict(self)


class DockerRequirement(Requirement):
    """
    Indicates that a workflow component should be run in a Docker container,
    and specifies how to fetch or build the image.

    Documentation: https://www.commonwl.org/v1.0/CommandLineTool.html#DockerRequirement
    """

    def __init__(self, docker_pull=None, docker_load=None, docker_file=None,
                 docker_import=None, docker_image_id=None, docker_output_dir=None):
        """
        :param docker_pull: image to retrive with docker pull
        :type docker_pull: STRING
        :param docker_load: HTTP URL from which to download Docker image
        :type docker_load: STRING
        :param docker_file: supply the contents of a Dockerfile
        :type docker_file: STRING
        :param docker_import: HTTP URL to download and gunzip a Docker images
        :type docker_import: STRING
        :param docker_image_id: Image id for docker run
        :type docker_image_id: STRING
        :param docker_output_dir: designated output dir inside the Docker container
        :type docker_output_dir: STRING
        """
        Requirement.__init__(self, 'DockerRequirement')
        self.dockerPull = docker_pull
        self.dockerLoad = docker_load
        self.dockerFile = docker_file
        self.dockerImport = docker_import
        self.dockerImageId = docker_image_id
        self.dockerOutputDir = docker_output_dir

    def get_dict(self):
        base = Requirement.get_dict(self)
        base.update({p: v for p, v in vars(self).items() if p.startswith('docker') and v is not None})
        return base


class EnvVarRequirement(Requirement):
    """
    Define a list of environment variables which will be set in the execution environment of the tool.
    See EnvironmentDef for details.

    Documentation: https://www.commonwl.org/v1.0/CommandLineTool.html#EnvVarRequirement
    """
    def __init__(self, env_def):
        """
        :param env_def: The list of environment variables.
        :type env_def: list[EnvironmentDef]
        """
        Requirement.__init__(self, 'ShellCommandRequirement')
        self.envDef = env_def

    def get_dict(self):
        base = Requirement.get_dict(self)
        base["envDef"] = [e.get_dict() for e in self.envDef]

    class EnvironmentDef(object):
        """
        Define an environment variable that will be set in the runtime environment
        by the workflow platform when executing the command line tool.
        May be the result of executing an expression, such as getting a parameter from input.

        Documentation: https://www.commonwl.org/v1.0/CommandLineTool.html#EnvironmentDef
        """
        def __init__(self, env_name, env_value):
            """
            :param env_name: The environment variable name
            :type env_name: STRING
            :param env_value: The environment variable value
            :type env_value: STRING
            """
            self.envName = env_name
            self.envValue = env_value

        def get_dict(self):
            return {"envName": self.envName, "envValue": self.envValue}


class ShellCommandRequirement(Requirement):
    """
    Modify the behavior of CommandLineTool to generate a single string containing a shell command line.

    Documentation: https://www.commonwl.org/v1.0/CommandLineTool.html#ShellCommandRequirement
    """

    def __init__(self):
        Requirement.__init__(self, 'ShellCommandRequirement')

    def get_dict(self):
        return Requirement.get_dict(self)


class ResourceRequirement(Requirement):
    """
    Specify basic hardware resource requirements.

    Documentation: https://www.commonwl.org/v1.0/CommandLineTool.html#ResourceRequirement
    """

    def __init__(self, cores_min=None, cores_max=None, ram_min=None, ram_max=None, tmpdir_min=None, tmpdir_max=None,
                 outdir_min=None, outdir_max=None):
        """
        :param cores_min: Minimum reserved number of CPU cores
        :type cores_min: string | float
        :param cores_max: Maximum reserved number of CPU cores
        :type cores_max: string | float
        :param ram_min: Minimum reserved RAM in mebibytes (2**20)
        :type ram_min: string | float
        :param ram_max: Maximum reserved RAM in mebibytes (2**20)
        :type ram_max: string | float
        :param tmpdir_min: Minimum reserved filesystem based storage for the designated temporary directory, in mebibytes (2**20)
        :type tmpdir_min: string | float
        :param tmpdir_max: Maximum reserved filesystem based storage for the designated temporary directory, in mebibytes (2**20)
        :type tmpdir_max: string | float
        :param outdir_min: Minimum reserved filesystem based storage for the designated output directory, in mebibytes (2**20)
        :type outdir_min: string | float
        :param outdir_max: Maximum reserved filesystem based storage for the designated output directory, in mebibytes (2**20)
        :type outdir_max: string | float
        """
        Requirement.__init__(self, 'ResourceRequirement')

        self.coresMin = cores_min
        self.coresMax = cores_max
        self.ramMin = ram_min
        self.ramMax = ram_max
        self.tmpdirMin = tmpdir_min
        self.tmpdirMax = tmpdir_max
        self.outdirMin = outdir_min
        self.outdirMax = outdir_max

    def get_dict(self):
        base = Requirement.get_dict(self)
        base.update({p: v for p, v in vars(self).items() if v is not None})
        return base

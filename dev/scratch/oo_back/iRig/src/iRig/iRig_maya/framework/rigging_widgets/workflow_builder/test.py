
from workflow.workflow_controller import WorkflowController

#controller = WorkflowController.get_controller()
import os
#print controller.get_project_directory()
import file_tools as ft

print ft.__path__

ez_path = ft.EzAs(
    PIPE_BASE=r'D:\pipeline\paxtong\dev\git_repo\dev_pipeline_prod',
    # PIPE_BASE='G:/Pipeline/pipeline',
    project='global_icon_show',
    TT_PROJCODE='LMM',
    TT_ENTNAME='Ariel',
    SERVER_BASE='Y:',
    TT_ASSTYPE='Character',
    TT_STEPCODE='fac',
    TT_PACKAGE='Maya',
    TT_USER=os.environ['USERNAME']
)

print ez_path
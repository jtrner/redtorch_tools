
import os
import sys
os.environ['PATH'] += ";G:/Pipeline/pipeline_external/plugins/alembic/1.7.9/lib"
sys.path.append("G:/Pipeline/pipeline_external/plugins/alembic/1.7.9/lib/python2.7/site-packages")
import abcdiff
thing = abcdiff.DiffWalker("C:/Users/kyles/Desktop/testa.abc", "C:/Users/kyles/Desktop/testb.abc")
thing.walk()
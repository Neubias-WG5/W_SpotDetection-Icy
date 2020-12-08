import os
import sys
from cytomine.models import *
from subprocess import call
from pathlib import Path

from biaflows import CLASS_SPTCNT
from biaflows.helpers import prepare_data, BiaflowsJob, upload_data, upload_metrics, get_discipline


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clean_icy_result_file(filepath, n=1):
    lines = None
    with open(filepath, "r") as file:
        lines = file.readlines()
    with open(filepath, "w") as file:
        file.writelines([l for l in lines[n:] if len(l.strip()) > 0])


def main():
    with BiaflowsJob.from_cli(sys.argv[1:]) as nj:
        nj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialization...")

        # 1. Create working directories on the machine:
        # 2. Download (or read) data
        problem_cls = get_discipline(nj, default=CLASS_SPTCNT)
        is_2d = True
        nj.job.update(progress=1, statusComment="Execute workflow on problem class '{}'".format(problem_cls))
        in_images, gt_images, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, nj, is_2d=is_2d, **nj.flags)

        # 3. Execute workflow
        scale3sens = nj.parameters.icy_scale3sensitivity
        nj.job.update(progress=25, statusComment="Launching workflow...")
        call("java -cp /icy/lib/ -jar /icy/icy.jar -hl", shell=True, cwd="/icy")
        call("java -cp /icy/lib/ -jar /icy/icy.jar -hl -x plugins.adufour.protocols.Protocols "
             "protocol=\"/icy/protocols/protocol.protocol\" inputFolder=\"{}\" outputFolder=\"{}\" extension=tif "
             "scale2enable=true scale2sensitivity={}".format(in_path, out_path, scale3sens), shell=True, cwd="/icy")

        # 3.5 Remove the xml-output files
        for p in Path(out_path).glob("*.xml"):
            p.unlink()
        
        # 4. Upload the annotation and labels to Cytomine
        upload_data(problem_cls, nj, in_images, out_path, **nj.flags, is_2d=is_2d, monitor_params={
           "start": 60, "end": 90, "period": 0.1
        })

        # 5. Compute and upload the metrics
        nj.job.update(progress=90, statusComment="Computing and uploading metrics...")
        upload_metrics(problem_cls, nj, in_images, gt_path, out_path, tmp_path, **nj.flags)

        nj.job.update(progress=100, status=Job.TERMINATED, status_comment="Finished.")


if __name__ == "__main__":
    main()

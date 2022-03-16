from nipype.interfaces.r import RCommand
from nipype.interfaces.base import (
    TraitedSpec,
    BaseInterface,
    BaseInterfaceInputSpec,
    File,
    traits,
)
import os
from string import Template


class LesionClustersInputSpec(BaseInterfaceInputSpec):
    prob_map = File(exists=True, mandatory=True)
    bin_map = File(exists=True, mandatory=True)
    centers = File("centers.nii.gz", usedefault=True)
    nnmap = File("nnmap.nii.gz", usedefault=True)
    clusmap = File("clusmap.nii.gz", usedefault=True)
    gmmmap = File("gmmmap.nii.gz", usedefault=True)
    gmm = traits.Bool(True, usedefault=True)
    parallel = traits.Bool(False, usedefault=True)
    cores = traits.Int(1, usedefault=True)
    smooth = traits.Float(1.2, usedefault=True)
    min_center_size = traits.Int(10, usedefault=True)


class LesionClustersOutputSpec(TraitedSpec):
    centers = File(exists=True)
    nnmap = File(exists=True)
    clusmap = File(exists=True)
    gmmmap = File(exists=False)


class LesionClusters(BaseInterface):
    input_spec = LesionClustersInputSpec
    output_spec = LesionClustersOutputSpec

    def _run_interface(self, runtime):
        script = self._cmdline(runtime)
        rcmd = RCommand(script=script, rfile=True)
        result = rcmd.run()
        return result.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["centers"] = os.path.abspath(self.inputs.centers)
        outputs["nnmap"] = os.path.abspath(self.inputs.nnmap)
        outputs["clusmap"] = os.path.abspath(self.inputs.clusmap)
        outputs["gmmmap"] = os.path.abspath(self.inputs.gmmmap)
        return outputs

    def _cmdline(self, runtime):
        d = dict(
            prob_map=self.inputs.prob_map,
            bin_map=self.inputs.bin_map,
            centers=self.inputs.centers,
            nnmap=self.inputs.nnmap,
            clusmap=self.inputs.clusmap,
            gmmmap=self.inputs.gmmmap,
            min_center_size=self.inputs.min_center_size,
            gmm="T" if self.inputs.gmm else "F",
            parallel="T" if self.inputs.parallel else "F",
            cores=self.inputs.cores,
        )
        script = Template(
            """
                library(neurobase)
                library(lesiontools)
                prob_map = readnii('$prob_map')
                lesion_map = readnii('$lesion_map')
                phase = readnii('$phase')
                lesionclusters = lesionclusters(prob_map, bin_map smooth=$smooth, minCenterSize=$min_center_size, gmm=$gmm, parallel=$parallel, cores=$cores)
                writenii(lesionclusters$$lesioncenters, "$centers")
                writenii(lesionclusters$$lesionclusters.nn, "$nnmap")
                writenii(lesionclusters$$lesionclusters.cc, "$clusmap")
                if ($gmm) {
                    writenii(lesionclusters$$lesionclusters.gmm, "$gmmmap")
                }
                """
        ).substitute(d)

        return script


if __name__ == "__main__":
    clusters = LesionClusters()
    clusters.inputs.prob_map = "prob_map.nii.gz"
    clusters.inputs.bin_map = "bin_map.nii.gz"
    clusters.inputs.centers = "centers.nii.gz"
    clusters.inputs.nnmap = "nnmap.nii.gz"
    clusters.inputs.clusmap = "clusmap.nii.gz"
    clusters.inputs.gmmmap = "gmmmap.nii.gz"
    clusters.inputs.gmm = True
    clusters.inputs.parallel = True
    clusters.inputs.cores = 4
    clusters.inputs.smooth = 1.2
    clusters.inputs.min_center_size = 10
    clusters.run()

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


class CVSInputSpec(BaseInterfaceInputSpec):
    t1 = File(exists=True, mandatory=True)
    epi = File(exists=True, mandatory=True)
    flair = File(exists=True, mandatory=True)
    mimosa_prob_map = File(exists=True, mandatory=True)
    mimosa_bin_map = File(exists=True, mandatory=True)
    candidate_lesions = File("candidate_lesions.npy", usedefault=True)
    cvs_prob_map = File("prob_map.npy", usedefault=True)
    biomarker = File("biomarker.npy", usedefault=True)
    parallel = traits.Bool(False, usedefault=True)
    skullstripped = traits.Bool(False, usedefault=True)
    biascorrected = traits.Bool(False, usedefault=True)
    c3d = traits.Bool(True, usedefault=True)
    cores = traits.Int(1, usedefault=True)


class CVSOutputSpec(TraitedSpec):
    candidate_lesions = File(exists=True)
    cvs_prob_map = File(exists=False)
    biomarker = File(exists=False)


class CVS(BaseInterface):
    input_spec = CVSInputSpec
    output_spec = CVSOutputSpec

    def _run_interface(self, runtime):
        script = self._cmdline(runtime)
        rcmd = RCommand(script=script, rfile=True)
        result = rcmd.run()
        return result.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["candidate_lesions"] = os.path.abspath(self.inputs.candidate_lesions)
        outputs["cvs_prob_map"] = os.path.abspath(self.inputs.cvs_prob_map)
        outputs["biomarker"] = os.path.abspath(self.inputs.biomarker)
        return outputs

    def _cmdline(self, runtime):
        d = dict(
            t1=self.inputs.t1,
            epi=self.inputs.epi,
            flair=self.inputs.flair,
            mimosa_prob_map=self.inputs.mimosa_prob_map,
            mimosa_bin_map=self.inputs.mimosa_bin_map,
            candidate_lesions=self.inputs.candidate_lesions,
            cvs_prob_map=self.inputs.cvs_prob_map,
            biomarker=self.inputs.biomarker,
            parallel="T" if self.inputs.parallel else "F",
            skullstripped="T" if self.inputs.skullstripped else "F",
            biascorrected="T" if self.inputs.biascorrected else "F",
            c3d="T" if self.inputs.c3d else "F",
            cores=self.inputs.cores,
        )
        script = Template(
            """
                library(neurobase)
                library(lesiontools)
                library(reticulate)
                np = import('numpy')
                t1 = readnii('$t1')
                flair = readnii('$flair')
                epi = readnii('$epi')
                mimosa_prob_map = readnii('$mimosa_prob_map')
                mimosa_bin_map = readnii('$mimosa_bin_map')
                result = centralveins(epi, t1, flair, probmap = mimosa_prob_map, binmap = mimosa_bin_map, parallel = $parallel, skullstripped = $skullstripped, biascorrected = $biascorrected, c3d = $c3d, cores = $cores)
                np$$save('$candidate_lesions', result$$candidate.lesions)
                np$$save('$cvs_prob_map', result$$cvs.probmap)
                np$$save('$biomarker', result$$cvs.biomarker)
                """
        ).substitute(d)

        return script


if __name__ == "__main__":
    cvs = CVS()
    cvs.inputs.t1 = "t1.nii.gz"
    cvs.inputs.flair = "flair.nii.gz"
    cvs.inputs.epi = "epi.nii.gz"
    cvs.inputs.mimosa_prob_map = "mimosa_prob_map.nii.gz"
    cvs.inputs.mimosa_bin_map = "mimosa_bin_map.nii.gz"
    cvs.inputs.candidate_lesions = "candidate_lesions.npy"
    cvs.inputs.cvs_prob_map = "prob_map.npy"
    cvs.inputs.biomarker = "biomarker.npy"
    cvs.inputs.parallel = False
    cvs.inputs.skullstripped = True
    cvs.inputs.biascorrected = True
    cvs.inputs.c3d = True
    cvs.inputs.cores = 1
    cvs.run()

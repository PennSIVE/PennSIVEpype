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


class MIMoSAdataInputSpec(BaseInterfaceInputSpec):
    brainmask = File(exists=False, mandatory=False)
    t1 = File(exists=True, mandatory=True)
    t2 = File(exists=True, mandatory=False)
    flair = File(exists=True, mandatory=True)
    pd = File(exists=True, mandatory=False)
    tissue = traits.Bool(False, usedefault=True)
    verbose = traits.Bool(False, usedefault=True)
    cores = traits.Int(1, usedefault=True)
    mimosa_dataframe = File("mimosa_dataframe.npy", usedefault=True)
    mimosa_candidate_mask = File("mimosa_candidate_mask.npy", usedefault=True)


class MIMoSAdataOutputSpec(TraitedSpec):
    mimosa_dataframe = File(exists=True)
    mimosa_candidate_mask = File(exists=True)


class MIMoSAdata(BaseInterface):
    input_spec = MIMoSAdataInputSpec
    output_spec = MIMoSAdataOutputSpec

    def _run_interface(self, runtime):
        script = self._cmdline(runtime)
        rcmd = RCommand(script=script, rfile=True)
        result = rcmd.run()
        return result.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["mimosa_dataframe"] = os.path.abspath(self.inputs.mimosa_dataframe)
        outputs["mimosa_candidate_mask"] = os.path.abspath(
            self.inputs.mimosa_candidate_mask
        )
        return outputs

    def _cmdline(self, runtime):
        d = dict(
            t1=self.inputs.t1,
            t2=self.inputs.t2,
            flair=self.inputs.flair,
            pd=self.inputs.pd,
            tissue="T" if self.inputs.tissue else "F",
            verbose="T" if self.inputs.verbose else "F",
            cores=self.inputs.cores,
            brainmask = self.inputs.brainmask,
            mimosa_dataframe = self.inputs.mimosa_dataframe,
            mimosa_candidate_mask = self.inputs.mimosa_candidate_mask
        )
        script = Template(
            """
            library(neurobase)
            library(mimosa)
            library(reticulate)
            np = import('numpy')
            t1 = readnii('$t1')
            flair = readnii('$flair')
            if (file.exists('$t2')) {
                t2 = readnii('$t2')
            } else {
                t2 = NULL
            }
            if (file.exists('$pd')) {
                pd = readnii('$pd')
            } else {
                pd = NULL
            }
            if (file.exists('$brainmask')) {
                brainmask = readnii('$brainmask')
            } else {
                brainmask = t1 > min(t1)
            }
            mimosa_testdata = mimosa_data(
                    brain_mask = brainmask,
                    FLAIR = flair,
                    T1 = t1,
                    T2 = t2,
                    PD = pd,
                    tissue = $tissue,
                    cores = $cores,
                    verbose = $verbose)
            
            mimosa_testdata_df = mimosa_testdata$$mimosa_dataframe
            mimosa_candidate_mask = mimosa_testdata$$top_voxels
            np$$save('$mimosa_dataframe', mimosa_testdata_df)
            np$$save('$mimosa_candidate_mask', mimosa_candidate_mask)
            """
        ).substitute(d)
            
        return script


if __name__ == "__main__":
    mimosa_data = MIMoSAdata()
    mimosa_data.inputs.t1 = "t1.nii.gz"
    mimosa_data.inputs.flair = "flair.nii.gz"
    mimosa_data.inputs.t2 = "t2.nii.gz"
    mimosa_data.inputs.pd = "pd.nii.gz"
    mimosa_data.inputs.tissue = True
    mimosa_data.inputs.verbose = True
    mimosa_data.inputs.cores = 1
    mimosa_data.run()

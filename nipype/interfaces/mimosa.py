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


class MIMoSAInputSpec(BaseInterfaceInputSpec):
    t1 = File(exists=True, mandatory=True)
    t2 = File(exists=True, mandatory=False)
    flair = File(exists=True, mandatory=True)
    pd = File(exists=True, mandatory=False)
    prob_map = File("prob_map.nii.gz", usedefault=True)
    tissue = traits.Bool(False, usedefault=True)
    verbose = traits.Bool(False, usedefault=True)
    cores = traits.Int(1, usedefault=True)


class MIMoSAOutputSpec(TraitedSpec):
    prob_map = File(exists=False)


class MIMoSA(BaseInterface):
    input_spec = MIMoSAInputSpec
    output_spec = MIMoSAOutputSpec

    def _run_interface(self, runtime):
        script = self._cmdline(runtime)
        rcmd = RCommand(script=script, rfile=True)
        result = rcmd.run()
        return result.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["prob_map"] = os.path.abspath(self.inputs.prob_map)
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
            prob_map = self.inputs.prob_map,
        )
        script = Template(
                """
                library(neurobase)
                library(mimosa)
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
                brainmask <- t1 > min(t1)
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

                predictions = predict(mimosa_model,
                                    newdata = mimosa_testdata_df,
                                    type = "response")


                probability_map = niftiarr(brainmask, 0)
                probability_map[mimosa_candidate_mask == 1] = predictions

                writenii(probability_map, '$prob_map')
                """
            ).substitute(d)

        return script

if __name__ == "__main__":
    mimosa = MIMoSA()
    mimosa.inputs.t1 = "t1.nii.gz"
    mimosa.inputs.flair = "flair.nii.gz"
    mimosa.inputs.t2 = "t2.nii.gz"
    mimosa.inputs.pd = "pd.nii.gz"
    mimosa.inputs.tissue = True
    mimosa.inputs.verbose = True
    mimosa.inputs.cores = 1
    mimosa.run()

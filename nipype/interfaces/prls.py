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


class PRLInputSpec(BaseInterfaceInputSpec):
    prob_map = File(exists=True, mandatory=True)
    lesion_map = File(exists=True, mandatory=True)
    phase = File(exists=True, mandatory=True)
    leslabels = File("leslabels.nii.gz", usedefault=True)
    preds = File("preds.npy", usedefault=True)
    disc = traits.Bool(True, usedefault=True)


class PRLOutputSpec(TraitedSpec):
    leslabels = File(exists=True)
    preds = File(exists=False)


class PRL(BaseInterface):
    input_spec = PRLInputSpec
    output_spec = PRLOutputSpec

    def _run_interface(self, runtime):
        script = self._cmdline(runtime)
        rcmd = RCommand(script=script, rfile=True)
        result = rcmd.run()
        return result.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["leslabels"] = os.path.abspath(self.inputs.leslabels)
        outputs["preds"] = os.path.abspath(self.inputs.preds)
        return outputs

    def _cmdline(self, runtime):
        d = dict(
            prob_map=self.inputs.prob_map,
            lesion_map=self.inputs.lesion_map,
            phase=self.inputs.phase,
            leslabels=self.inputs.leslabels,
            preds=self.inputs.preds,
            disc="T" if self.inputs.disc else "F",
        )
        script = Template(
            """
                library(neurobase)
                library(fslr)
                library(prlr)
                library(reticulate)
                np = import('numpy')
                prob_map = readnii('$prob_map')
                lesion_map = readnii('$lesion_map')
                phase = readnii('$phase')
                result = findprls(probmap = prob_map, lesmask = lesion_map, phasefile = phase, disc = $disc)
                np$$save('$preds', result$$preds)
                writenii(result$$leslabels, '$leslabels')
                """
        ).substitute(d)

        return script


if __name__ == "__main__":
    prl = PRL()
    prl.inputs.prob_map = "prob_map.nii.gz"
    prl.inputs.lesion_map = "lesion_map.nii.gz"
    prl.inputs.phase = "phase.nii.gz"
    prl.inputs.disc = True
    prl.run()

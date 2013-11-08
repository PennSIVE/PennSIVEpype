# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from nipype.testing import assert_equal
from nipype.interfaces.slicer.filtering.checkerboardfilter import CheckerBoardFilter
def test_CheckerBoardFilter_inputs():
    input_map = dict(ignore_exception=dict(nohash=True,
    usedefault=True,
    ),
    outputVolume=dict(position=-1,
    hash_files=False,
    argstr='%s',
    ),
    args=dict(argstr='%s',
    ),
    inputVolume2=dict(position=-2,
    argstr='%s',
    ),
    inputVolume1=dict(position=-3,
    argstr='%s',
    ),
    terminal_output=dict(mandatory=True,
    nohash=True,
    ),
    environ=dict(nohash=True,
    usedefault=True,
    ),
    checkerPattern=dict(argstr='--checkerPattern %s',
    sep=',',
    ),
    )
    inputs = CheckerBoardFilter.input_spec()

    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(inputs.traits()[key], metakey), value
def test_CheckerBoardFilter_outputs():
    output_map = dict(outputVolume=dict(position=-1,
    ),
    )
    outputs = CheckerBoardFilter.output_spec()

    for key, metadata in output_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(outputs.traits()[key], metakey), value
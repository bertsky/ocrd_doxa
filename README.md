[![PyPI version](https://badge.fury.io/py/ocrd-doxa.svg)](https://badge.fury.io/py/ocrd-doxa)
[![Docker Image CD](https://github.com/bertsky/ocrd_doxa/actions/workflows/docker-image.yml/badge.svg)](https://github.com/bertsky/ocrd_doxa/actions/workflows/docker-image.yml)

# ocrd_wrap

    OCR-D wrapper for DoxaPy image binarization via locally adaptive thresholding

  * [Introduction](#introduction)
  * [Installation](#installation)
  * [Usage](#usage)
     * [OCR-D processor interface ocrd-doxa-binarize](#ocr-d-processor-interface-ocrd-doxa-binarize)
  * [Testing](#testing)


## Introduction

This offers [OCR-D](https://ocr-d.de) compliant [workspace processors](https://ocr-d.de/en/spec/cli) for
binarization via [Doxa](https://github.com/brandonmpetty/Doxa) (using its native [Python bindings](https://github.com/brandonmpetty/Doxa/tree/master/Bindings/Python)).

It is itself written in Python, and relies heavily on the
[OCR-D core API](https://github.com/OCR-D/core). This is
responsible for handling METS/PAGE, and providing the OCR-D
CLI.

## Installation

Create and activate a [virtual environment](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) as usual.

To install Python dependencies:

    make deps

Which is the equivalent of:

    pip install -r requirements.txt

To install this module, then do:

    make install

Which is the equivalent of:

    pip install .

## Usage

### [OCR-D processor](https://ocr-d.github.io/cli) interface `ocrd-doxa-binarize`

To be used with [PAGE-XML](https://github.com/PRImA-Research-Lab/PAGE-XML) documents in an [OCR-D](https://ocr-d.github.io/) annotation workflow.

```
ocrd-doxa-binarize -h

Usage: ocrd-doxa-binarize [OPTIONS]

  binarize via locally adaptive thresholding

Options:
  -I, --input-file-grp USE        File group(s) used as input
  -O, --output-file-grp USE       File group(s) used as output
  -g, --page-id ID                Physical page ID(s) to process
  --overwrite                     Remove existing output pages/images
                                  (with --page-id, remove only those)
  -p, --parameter JSON-PATH       Parameters, either verbatim JSON string
                                  or JSON file path
  -P, --param-override KEY VAL    Override a single JSON object key-value pair,
                                  taking precedence over --parameter
  -m, --mets URL-PATH             URL or file path of METS to process
  -w, --working-dir PATH          Working directory of local workspace
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Log level
  -C, --show-resource RESNAME     Dump the content of processor resource RESNAME
  -L, --list-resources            List names of processor resources
  -J, --dump-json                 Dump tool description as JSON and exit
  -h, --help                      This help message
  -V, --version                   Show version

Parameters:
   "dpi" [number - 0]
    pixel density in dots per inch (overrides any meta-data in the
    images); disabled when zero
   "level-of-operation" [string - "page"]
    PAGE XML hierarchy level to operate on
    Possible values: ["page", "region", "line"]
   "algorithm" [string - "ISauvola"]
    Thresholding algorithm to use.
    Possible values: ["Otsu", "Bernsen", "Niblack", "Sauvola", "Wolf",
    "Gatos", "NICK", "Su", "Singh", "Bataineh", "ISauvola", "WAN"]
   "parameters" [object - {}]
    Dictionary of algorithm-specific parameters. Unless overridden here,
    the following defaults are used:
	Bernsen:        {'window': 75, 'threshold': 100, 'contrast-limit': 25}
	NICK:           {'window': 75, 'k': -0.2}
	Niblack:        {'window': 75, 'k': 0.2}
	Singh:          {'window': 75, 'k', 0.2}
	Gatos:          {'glyph': 60}
	Sauvola:        {'window': 75, 'k': 0.2}
	Wolf:           {'window': 75, 'k': 0.2}
	WAN:            {'window': 75, 'k': 0.2}
	Su:             {'window': 0 (based on stroke size), 
                     'minN':  windowSize (roughly based on size of window)}

   (window/glyph sizes are in px, threshold/limits in uint8 [0,255])
```

## Testing

none yet


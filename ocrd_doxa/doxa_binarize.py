from __future__ import absolute_import

import os.path
from PIL import Image
import numpy as np
import doxapy

from ocrd import Processor
from ocrd_utils import (
    getLogger,
    make_file_id,
    assert_file_grp_cardinality,
    MIMETYPE_PAGE
)
from ocrd_modelfactory import page_from_file
from ocrd_models.ocrd_page import (
    LabelType, LabelsType,
    MetadataItemType,
    AlternativeImageType,
    to_xml
)
from .config import OCRD_TOOL

TOOL = 'ocrd-doxa-binarize'

class DoxaBinarize(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools'][TOOL]
        kwargs['version'] = OCRD_TOOL['version']
        super(DoxaBinarize, self).__init__(*args, **kwargs)
    
    def process(self):
        """Performs binarization of segment or page images with DoxaPy on the workspace.
        
        Open and deserialize PAGE input files and their respective images,
        then iterate over the element hierarchy down to the requested
        ``level-of-operation`` in the element hierarchy.
        
        For each segment element, retrieve a segment image according to
        the layout annotation (from an existing AlternativeImage, or by
        cropping via coordinates into the higher-level image, and -
        when applicable - deskewing).
        
        Next, binarize the image according to ``algorithm`` with DoxaPy.
        
        Then write the new image to the workspace along with the output fileGrp,
        and using a file ID with suffix ``.IMG-BIN`` with further identification
        of the input element.
        
        Produce a new PAGE output file by serialising the resulting hierarchy.
        """
        LOG = getLogger('processor.DoxaBinarize')
        oplevel = self.parameter['level-of-operation']
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)
        
        for (n, input_file) in enumerate(self.input_files):
            file_id = make_file_id(input_file, self.output_file_grp)
            page_id = input_file.pageId or input_file.ID
            LOG.info("INPUT FILE %i / %s", n, page_id)
            
            pcgts = page_from_file(self.workspace.download_file(input_file))
            page = pcgts.get_Page()
            metadata = pcgts.get_Metadata() # ensured by from_file()
            metadata.add_MetadataItem(
                MetadataItemType(type_="processingStep",
                                 name=self.ocrd_tool['steps'][0],
                                 value=TOOL,
                                 Labels=[LabelsType(
                                     externalModel="ocrd-tool",
                                     externalId="parameters",
                                     Label=[LabelType(type_=name,
                                                      value=self.parameter[name])
                                            for name in self.parameter.keys()])]))
            
            for page in [page]:
                page_image, page_coords, page_image_info = self.workspace.image_from_page(
                    page, page_id, feature_filter='binarized')
                if self.parameter['dpi'] > 0:
                    dpi = self.parameter['dpi']
                    LOG.info("Page '%s' images will use %d DPI from parameter override", page_id, dpi)
                elif page_image_info.resolution != 1:
                    dpi = page_image_info.resolution
                    if page_image_info.resolutionUnit == 'cm':
                        dpi = round(dpi * 2.54)
                    LOG.info("Page '%s' images will use %d DPI from image meta-data", page_id, dpi)
                else:
                    dpi = 300
                    LOG.info("Page '%s' images will use 300 DPI from fall-back", page_id)
                
                if oplevel == 'page':
                    self._process_segment(page, page_image, page_coords,
                                          "page '%s'" % page_id, input_file.pageId,
                                          file_id + '.IMG-BIN')
                    continue
                regions = page.get_AllRegions(classes=['Text'])
                if not regions:
                    LOG.warning("Page '%s' contains no text regions", page_id)
                for region in regions:
                    region_image, region_coords = self.workspace.image_from_segment(
                        region, page_image, page_coords, feature_filter='binarized')
                    if oplevel == 'region':
                        self._process_segment(region, region_image, region_coords,
                                              "region '%s'" % region.id, None,
                                              file_id + '.IMG-BIN_' + region.id)
                        continue
                    lines = region.get_TextLine()
                    if not lines:
                        LOG.warning("Region '%s' contains no text lines", region.id)
                    for line in lines:
                        line_image, line_coords = self.workspace.image_from_segment(
                            line, region_image, region_coords, feature_filter='binarized')
                        self._process_segment(line, line_image, line_coords,
                                              "line '%s'" % line.id, None,
                                              file_id + '.IMG-BIN_' + line.id)
            
            pcgts.set_pcGtsId(file_id)
            self.workspace.add_file(
                ID=file_id,
                file_grp=self.output_file_grp,
                pageId=input_file.pageId,
                mimetype=MIMETYPE_PAGE,
                local_filename=os.path.join(self.output_file_grp,
                                            file_id + '.xml'),
                content=to_xml(pcgts))
    
    def _process_segment(self, segment, image, coords, where, page_id, file_id):
        LOG = getLogger('processor.DoxaBinarize')
        features = coords['features'] # features already applied to image
        features += ',binarized'
        array = np.array(image.convert('L'))
        algorithm = self.parameter['algorithm']
        algorithm = {"Otsu": doxapy.Binarization.Algorithms.OTSU,
                     "Bernsen": doxapy.Binarization.Algorithms.BERNSEN,
                     "Niblack": doxapy.Binarization.Algorithms.NIBLACK,
                     "Sauvola": doxapy.Binarization.Algorithms.SAUVOLA,
                     "Wolf": doxapy.Binarization.Algorithms.WOLF,
                     "Gatos": doxapy.Binarization.Algorithms.GATOS,
                     "NICK": doxapy.Binarization.Algorithms.NICK,
                     "Su": doxapy.Binarization.Algorithms.SU,
                     "Singh": doxapy.Binarization.Algorithms.TRSINGH,
                     "Bataineh": doxapy.Binarization.Algorithms.BATAINEH,
                     "ISauvola": doxapy.Binarization.Algorithms.ISAUVOLA,
                     "WAN": doxapy.Binarization.Algorithms.WAN,
                     }.get(algorithm)
        doxapy.Binarization.update_to_binary(algorithm, array, self.parameter['parameters'])
        image = Image.fromarray(array)
        # annotate results
        file_path = self.workspace.save_image_file(
            image,
            file_id,
            file_grp=self.output_file_grp,
            page_id=page_id)
        segment.add_AlternativeImage(AlternativeImageType(
            filename=file_path, comments=features))
        LOG.debug("Binarized image for %s saved as '%s'", where, file_path)

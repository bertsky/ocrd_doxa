from __future__ import absolute_import

import os.path
from typing import Optional
from PIL import Image

import numpy as np
import doxapy

from ocrd import Processor, OcrdPageResult, OcrdPageResultImage
from ocrd_models.ocrd_page import (
    AlternativeImageType,
    PageType,
    OcrdPage
)


class DoxaBinarize(Processor):
    @property
    def executable(self):
        return 'ocrd-doxa-binarize'
    
    def process_page_pcgts(self, *input_pcgts: Optional[OcrdPage], page_id: Optional[str] = None) -> OcrdPageResult:
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
        pcgts = input_pcgts[0]
        result = OcrdPageResult(pcgts)
        oplevel = self.parameter['level-of-operation']
        page = pcgts.get_Page()
        for page in [page]:
            page_image, page_coords, page_image_info = self.workspace.image_from_page(
                page, page_id, feature_filter='binarized')
            if self.parameter['dpi'] > 0:
                dpi = self.parameter['dpi']
                self.logger.info("Page '%s' images will use %d DPI from parameter override", page_id, dpi)
            elif page_image_info.resolution != 1:
                dpi = page_image_info.resolution
                if page_image_info.resolutionUnit == 'cm':
                    dpi = round(dpi * 2.54)
                self.logger.info("Page '%s' images will use %d DPI from image meta-data", page_id, dpi)
            else:
                dpi = 300
                self.logger.info("Page '%s' images will use 300 DPI from fall-back", page_id)

            if oplevel == 'page':
                result.images.append(
                    self._process_segment(page, page_image, page_coords,
                                          "page '%s'" % page_id)
                )
                continue
            regions = page.get_AllRegions(classes=['Text'])
            if not regions:
                self.logger.warning("Page '%s' contains no text regions", page_id)
            for region in regions:
                region_image, region_coords = self.workspace.image_from_segment(
                    region, page_image, page_coords, feature_filter='binarized')
                if oplevel == 'region':
                    result.images.append(
                        self._process_segment(region, region_image, region_coords,
                                              "region '%s'" % region.id)
                        )
                    continue
                lines = region.get_TextLine()
                if not lines:
                    self.logger.warning("Region '%s' contains no text lines", region.id)
                for line in lines:
                    line_image, line_coords = self.workspace.image_from_segment(
                        line, region_image, region_coords, feature_filter='binarized')
                    result.images.append(
                        self._process_segment(line, line_image, line_coords,
                                              "line '%s'" % line.id)
                    )
        return result
    
    def _process_segment(self, segment, image, coords, where):
        features = coords['features'] or '' # features already applied to image
        if features:
            features += ','
        features += 'binarized'
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
        # crashes (Fatal Python error: Aborted) with allocation and segfault:
        #doxapy.Binarization.update_to_binary(algorithm, array, self.parameter['parameters'])
        #image = Image.fromarray(array)
        # crashes less often:
        binary = np.empty(array.shape, array.dtype)
        binarizer = doxapy.Binarization(algorithm)
        binarizer.initialize(array)
        binarizer.to_binary(binary, self.parameter['parameters'])
        image = Image.fromarray(np.array(binary))
        # annotate results
        image_ref = AlternativeImageType(comments=features)
        segment.add_AlternativeImage(image_ref)
        suffix = '' if isinstance(segment, PageType) else segment.id
        suffix += '.IMG-BIN'
        return OcrdPageResultImage(image, suffix, image_ref)

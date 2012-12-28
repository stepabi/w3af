'''
swf.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import zlib

from core.data.parsers.baseparser import BaseParser


class SWFParser(BaseParser):
    '''
    This class is a SWF (flash) parser which just focuses on extracting URLs.
    
    The parser is based on "SWF File Format Specification Version 10"
    http://www.adobe.com/content/dam/Adobe/en/devnet/swf/pdf/swf_file_format_spec_v10.pdf

    @author: Andres Riancho (andres.riancho@gmail.com)
    '''
    def __init__(self, HTTPResponse):
        BaseParser.__init__(self, HTTPResponse)

        swf = HTTPResponse.get_body()
        if self._is_compressed(swf):
            try:
                swf = self._inflate(swf)
            except Exception:
                # If the inflate fails... there is nothing else to do.
                return

        self._parse(swf)

    def _is_compressed(self, swf_document):
        '''

        @param swf_content: The SWF file.
        @return: True if the SWF is compressed
        '''
        return swf_document.startswith('CWS')

    def _inflate(self, swf_document):
        '''
        zlib.inflate the SWF file.

        @param swf_content: The SWF file.
        @return: A decompressed version of the SWF
        '''
        compressed_data = swf_document[8:]
        try:
            uncompressed_data = zlib.decompress(compressed_data)
        except zlib.error, e:
            raise Exception('Failed to inflate: ' + str(e))
        else:
            # TODO: Strings in SWF are NULL-Byte delimited. Maybe we can
            # use that to extract strings and apply regular expressions
            # more carefully?
            return uncompressed_data

    def _parse(self, swf_body):
        '''
        Parse the SWF bytecode.
        For now... don't decompile anything, just apply regular
        expressions to it.

        @param swf_body: SWF bytecode string
        '''
        self._regex_url_parse(swf_body)

    def get_references(self):
        '''
        Searches for references on a page. w3af searches references in every
        html tag, including:
            - a
            - forms
            - images
            - frames
            - etc.

        @return: Two lists, one with the parsed URLs, and one with the URLs
                 that came out of a regular expression. The second list if less
                 trustworthy.
        '''
        return ([], list(self._re_urls))

    def _return_empty_list(self, *args, **kwds):
        '''
        This method is called (see below) when the caller invokes one of:
            - get_forms
            - get_comments
            - get_meta_redir
            - get_meta_tags
            - get_references_of_tag

        @return: Because we are a PDF document, we don't have the same things that
        a nice HTML document has, so we simply return an empty list.
        '''
        return []

    get_references_of_tag = get_forms = get_comments = _return_empty_list
    get_meta_redir = get_meta_tags = _return_empty_list
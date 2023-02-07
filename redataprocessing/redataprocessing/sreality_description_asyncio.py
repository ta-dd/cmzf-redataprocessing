"""Example NumPy style docstrings.

This module demonstrates documentation as specified by the `NumPy
Documentation HOWTO`_. Docstrings may extend over multiple lines. Sections
are created with a section header followed by an underline of equal length.

Example
-------
Examples can be given using either the ``Example`` or ``Examples``
sections. Sections support any reStructuredText formatting, including
literal blocks::

    $ python example_numpy.py


Section breaks are created with two blank lines. Section breaks are also
implicitly created anytime a new section starts. Section bodies *may* be
indented:

Notes
-----
    This is an example of an indented section. It's like any other section,
    but the body is indented to help it stand out from surrounding text.

If a section is indented, then a section break is created by
resuming unindented text.

Attributes
----------
module_level_variable1 : int
    Module level variables may be documented in either the ``Attributes``
    section of the module docstring, or in an inline docstring immediately
    following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.


.. _NumPy Documentation HOWTO:
   https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

"""

import asyncio
import aiohttp
import ssl
import certifi

import nest_asyncio

# async download of offer description
nest_asyncio.apply()

async def get_response(session, url):
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    try:
        async with session.get(url, ssl=sslcontext) as response:
            response_text =  await response.json()
            #here response can be processed further
            return response_text

    except aiohttp.ClientError as e:
        return f"Error occured for {url} : {e}"

async def main(urls, chunk_size):
    async with aiohttp.ClientSession() as session: 
        all_responses=[]
        chunks = [urls[i:i+chunk_size] for i in range(0, len(urls), chunk_size)]

        for chunk_idx, chunk in enumerate(chunks):
            #here you process first batch -> request go async

            tasks = [get_response(session, url) for url in chunk]
            #here they come together
            responses = await asyncio.gather(*tasks)

            print(f'downloaded description of offers: {(chunk_idx+1)*chunk_size} out of {len(urls)}')
            
            #here we sqlite can be used
            #to name each observation you could use: response["_embedded"]["favourite"]["_links"]["self"]["href"][17:]
            all_responses=all_responses+responses
        return all_responses # returns list

def get_responses(urls, workers=5):
    """

    Parameters
    ----------
    urls :
        
    workers :
         (Default value = 5)

    Returns
    -------

    """
    loop = asyncio.get_event_loop()
    output_list = loop.run_until_complete(main(urls, workers))
    
    # Getting rid of NaN rows
    output_list = [i for i in output_list if i not in [item for item in output_list if len(item) == 1]]
    return output_list

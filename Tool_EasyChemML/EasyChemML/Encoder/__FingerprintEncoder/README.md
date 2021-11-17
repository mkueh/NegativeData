**Fingerprint-Encoder**

The Fingerprint Encoder transforms SMILES into different fingerprint

__the following fingerprints are supported:__

###### All settings that are also described on the linked web site can be entered as parameters. For example, the most important ones are given here

    For the length of the fingerprints all RDkit parameters for length (nbits, size, etc.) were changed to length
    
    rdkit  (http://rdkit.org/docs/source/rdkit.Chem.rdmolops.html)
        -- minPath
        -- maxPath
        -- length
        -- nBitsPerHash
        -- useHs (True/False)
        -- branchedPaths (True/False)
        -- ..
    morgan_circular   (https://www.rdkit.org/docs/source/rdkit.Chem.rdMolDescriptors.html)
        -- radius
        -- length
        -- useChirality (True/False)
        -- ..
    avalon  (https://www.rdkit.org/docs/source/rdkit.Avalon.pyAvalonTools.html)
        -- length
        -- ..
    layerdfingerprint  (http://rdkit.org/docs/source/rdkit.Chem.rdmolops.html)
        -- minPath
        -- maxPath
        -- length
        -- ..
    maccs (http://rdkit.org/docs/source/rdkit.Chem.MACCSkeys.html)
        -- ..
    atom_pairs (https://www.rdkit.org/docs/source/rdkit.Chem.rdMolDescriptors.html)
        -- minPath
        -- maxPath
        -- length
        -- ..
    topological_torsions (https://www.rdkit.org/docs/source/rdkit.Chem.rdMolDescriptors.html)
        -- length
        -- targetSize
        -- ..

**Setup in the Settings File**

    Examples:
    
    -   encoder_settings:{encoder: e_fpc, encoder_settings: 
        {
        fingerprints: [{fp_name: rdkit,  fpsize:128}]
        }
    
If multiple items are passed to the fingerprints list, a combination of all specified fingerprints is created as encoding
    
    -   encoder_settings:{encoder: e_fpc, encoder_settings: 
        {
        fingerprints: [
            {fp_name: rdkit,  fpsize : 128} , 
            {fp_name: rdkit,  fpsize : 256} ,
            {fp_name: morgan_circular,  radius : 4} 
        ]
        }
  
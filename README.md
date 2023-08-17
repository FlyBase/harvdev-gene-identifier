# gene-identifier
You need to get the original code first, we could do this in the docker file but by doing it here we just do it once and we may want to change something in those repos but have no permissions so can edit after downloading.
git clone https://huggingface.co/cgrivaz/FlyBaseGeneAbstractClassifier.git
git clone https://github.com/grivaz/FlyBaseAnnotationHelper.git

We probably need to have more general names for input, currently the fb_synonym_fb_2022_02.tsv file is actually the fb_synonym_fb_2023_04_modified_for_spreadsheets.tsv file
%% Setup
% General environment
candidates_folder = '/gpfs/offline1/staff/common/alfpet/git/lattice_design/candidates/';

% Lattice specific data
lattice_version = 'v01-01-03-01';
date = '260925';
lattice_name = ['m4U-' date '-' lattice_version]
ver = 'v1'; % Lattice version suffix for elements

description = 'Linear match of v01-01-01-01 with the TDR-1 fractional tunes (version 2)'

% Load the ACHROMAT 
lattice_folder = replace(lattice_version, '-', '_');
load([candidates_folder lattice_folder '/achro.mat'])
ACHRO = RING';
                      
% If necessary, fix missing NumIntSteps
ACHRO = mod_IntSteps(ACHRO,10,10,3,1); 

% Initialize physical apertures
L_und = 4.0; % in-vacuum undulator length

S_max = findspos(ACHRO,length(ACHRO)+1);
for i=1:length(ACHRO)
    S=findspos(ACHRO,i);
    if ( (S<L_und/2)||(S>=(S_max-L_und/2)))
        ACHRO{i}.EApertures=[0.011 0.002];
    else
        ACHRO{i}.EApertures=[0.011 0.011];
    end
end

% Load standard cLoptions
clear('cLoptions');
load('/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/m4U_260411_n01_43_01_01/m4U_260411_n01_43_01_01.mat')
cLoptions = m4U_260411_n01_43_01_01.cLoptions;

cLoptions.nseeds = 10;

cLoptions.All_famsO={}; %   optional
cLoptions.ringtune_fams = {'Q1';'Q2'};   % magnet families for tune matching
cLoptions.chrom_fams    = {'S3','S4'}; % magnet families for chromaticity matching
cLoptions.sext_fams     = {'S1';'S2';'S3';'S4'}; % list of all sextupole families 
cLoptions.RBfams        = {'R1'}; % reverse bend families

% Append lattice version suffix
for fams = {'ringtune_fams', 'chrom_fams', 'sext_fams', 'RBfams'}
    for i = 1:length(cLoptions.(fams{1}))
        cLoptions.(fams{1})(i) = {[cLoptions.(fams{1}){i} '_' ver]};
    end
end

% load('/gpfs/offline1/staff/common/alfpet/git/at/MAX4U/MagnetStrengthLimits.mat')
load('/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/m4_standard/m4_standard.mat')
ACHRO_ref = m4_standard.ACHROMAT;
V0 = 'auto';
bh = 'auto';

%% Run cLatt options
% m4UT = m4Uc_Latt(ACHRO,lattname,desc,cLoptions,ACHRO_ref,MagnetStrengthLimits,'V0',V0,'bh',bh,'basonly');
% m4UT = m4Uc_Latt(ACHRO,lattname,desc,cLoptions,ACHRO_ref,'V0',V0,'bh',bh);

m4UT = m4Uc_Latt(ACHRO,lattice_name,description,cLoptions,ACHRO_ref,...
    'corchro',true,'V0',V0,'bh',bh,'basplus','nodiag',true);

% Below an example of how the 'plotLatt' function can be used to produce
% plots from the m4UT structure and save the results on a file.
%
% plotLatt(m4UT,'all','ymaxplot_dm',0.004,'zoom',2.0,'ymaxplot',0.004,'xminplot',-0.010,'xmaxplot',0.01,'dpminplotLMA',-0.25,'dpmaxplotLMA',0.25,'caxrange',[-10 0],'caxrange_r',[-10 -5],'nogrid');
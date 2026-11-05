%% Input argument parsing
verboselevel = 4;
%% Setup
% General environment
candidates_folder = '/gpfs/offline1/staff/common/alfpet/git/lattice_design/candidates/';

% Lattice specific data
lattice_version = 'v01-02-01-01';
date = '261102';
lattice_name = ['m4U-' date '-' lattice_version];
ver = 'v1'; % Lattice version suffix for elements

description = 'Longitudinal gradient bend lattice starting from v01_01_03_01.';

% Load the ACHROMAT 
lattice_folder = replace(lattice_version, '-', '_');
load([candidates_folder lattice_folder '/achro.mat'])
ACHRO = RING';
                      
% If necessary, fix missing NumIntSteps
ACHRO = mod_IntSteps(ACHRO,10,10,3,1); 

% Initialize physical apertures
for i=2:length(ACHRO)
    ACHRO{i}.EApertures=[20.0 20.0]*1E-3;
    ACHRO{i}.RApertures=[-20.0 20.0 -20.0 20.0]*1e-3;
end


% Load standard cLoptions
clear('cLoptions');
load('/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/m4U_260411_n01_43_01_01/m4U_260411_n01_43_01_01.mat')
cLoptions = m4U_260411_n01_43_01_01.cLoptions;

cLoptions.nseeds = 10;

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

cLoptions.DAoptions.chroms0 = [2 2]/20.0;
cLoptions.DAoptions.DAmode = 'border';
cLoptions.MAoptions.acdprange=0.01;

cLoptions.APoptions.VClim      = true;
cLoptions.APoptions.VClimfact  = 1.0;
cLoptions.APoptions.SLKlim     = false;
cLoptions.APoptions.SLKlimfact = 1.0;
cLoptions.APoptions.DKlim      = false;
cLoptions.APoptions.DKlimfact  = 1.0;
cLoptions.APoptions.VClimfile  = 'VC_R3.txt';
cLoptions.APoptions.SLKlimfile = '';
cLoptions.APoptions.DKlimfile  = '';

cLoptions.sumTabfams = {'D1_v1';'D2_v1';'';...
                        'Q1_v1';'Q2_v1';'Q3_v1';'';'';'';'';...
                        'R1_v1';'';'';...
                        'S1_v1';'S2_v1';'S3_v1';'S4_v1';'';'';...
                        'O1_v1';'O2_v1';'O3_v1';...
                        '';'';...
                        '';'';'';'';'';''...
                         };

  cLoptions.eqsumTabfams = {'dipm';'dip';'';...
                            'Qfend';'Qdend';'Qfm_1';'';'';'';'';...
                            'Rb_U1_2';'';'';...
                            'Sdend';'Sfm';'Sd';'Sfi';'';'';...
                            'Oxx';'Oxy';'Oyy';...
                            '';''; ...
                            '';'';'';'';'';''...
                            };
 
 LatticeOptData.sumTabsca  = [2 5 0 ...
                              1 1 1 0 0 0 0 ...
                              1 0 0 ...
                              2 2 2 2 0 0 ...
                              2 2 2 ...
                              0 0 ...
                              0 0 0 0 0 0];


cLoptions.ErrorModel    = errormodel_Reduced('gdran',1.0,...
                            'mgalran',1.0,'mulsys',1.0,'mulran',1.0, ...
                            'strran',1.0,'bpmran',1.0, 'sagran', 1.0);
cLoptions.OCoptions.Niter = 100;

%% Loads refeence lattice
load('/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/m4_standard/m4_standard.mat')
ACHRO_ref = m4_standard.ACHROMAT;

%% Sets RF voltage
% V0 = 1.0E6;
V0 = 'auto';
bh = 'auto';

%% Run cLatt options
m4UT = m4Uc_Latt(ACHRO,lattice_name,description,cLoptions,ACHRO_ref,...
    'corchro',true,'V0',V0,'bh',bh,'basplus','nodiag',true, ...
    'noIBS', 'verbose', verboselevel-1);

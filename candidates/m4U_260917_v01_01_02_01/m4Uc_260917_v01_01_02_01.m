%% m4Uc_Template
% This script is a template to set up variables needed
% to run the "m4U_cLatt" function, which in turn, runs all "cLatt" function 
% options in a series of steps creating/overwriting a structure named
% "m4UT" in the matlab workspace, saving this variable
% in a "m4UT.mat" file and saving all matlab output in a logfile
%
% The intended workflow is 
%  1. Edit the statements in the "Lattice Specific Data" section below.
%  3. Run the script.
%  4. Rename or copy the resulting "m4UT" structure accordingly.
%  5. Execution may be interrupted at any moment and the most recent 
%     m4UT scruture can be recovered by loading it from the file 
%     saved on disk. From that point on, further calculation and 
%     updates to the m4UT structure may be carried out by running 
%     cLatt with specific input options. See the m4Uc_Latt script for 
%     many possible calls to cLatt.
%  
% The structure "cLoptions" is stored as a field in the "m4UT" structure 
% and contains various optional lattice evaluation settings. These are
% listed in the "General initialisation" section of the m4Uc_Latt function 
% (which sets their default values). If values different from the defaults 
% are desired for fields in the cLoptions structure, these can be changed 
% at anytime, e.g., by directly editing the correspondig fields or by 
% typing:
%    >>cLpptions = m4UT.cLoptions; % extracts cLoptions to the workspace.
%    >>cLoptions.DAoptions.nturns = 2028 % implementi the desired changes -
%    in this example, we change the number of turns used in dynamic
%    aperture calculations
%
%    >>m4UT=cLatt(m4UT, 'cLoptions',cLoptions,'verbose',1); % stores the
%                                          changes in the "m4UT" structure.
%    Note that such changes do not automatically re-run any evaluations 
%    that are affected by them - these need to be rerun explicitly 
%    to update the corresponding fields in the m4UT structure, e.g.
%
%    >> m4UT = cLatt(m4UT,'DAxy','verbose',2);
%    
% A quick look at the m4Uc_Latt function reveals the syntax of calls to
%  the cLatt function

%% Lattice specific data
lattname = 'm4U-260917-v01-01-02-01';
desc = 'Linear match of v01_01_01_01 with the TDR-1 fractional tunes';
ver = 'v1'; % Lattice version suffix for elements

% run or load the ACHROMAT 
filename = replace(lattname, '-', '_');
load(['/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/' filename '/' filename '_achro.mat'])
ACHRO = RING';
                      
% If necessary, fix missing NumIntSteps
ACHRO = mod_IntSteps(ACHRO,10,10,3,1); 

% Initialize physical apertures
for i=1:length(ACHRO)
    ACHRO{i}.EApertures=[0.011 0.011];
end

clear('cLoptions');
load('/gpfs/offline1/staff/common/alfpet/git/Max4U/CandidateLattices/m4U_260411_n01_43_01_01/m4U_260411_n01_43_01_01.mat')
cLoptions = m4U_260411_n01_43_01_01.cLoptions;

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
m4UT = m4Uc_Latt(ACHRO,lattname,desc,cLoptions,ACHRO_ref,'V0',V0,'bh',bh);

% Below an example of how the 'plotLatt' function can be used to produce
% plots from the m4UT structure and save the results on a file.
%
% plotLatt(m4UT,'all','ymaxplot_dm',0.004,'zoom',2.0,'ymaxplot',0.004,'xminplot',-0.010,'xmaxplot',0.01,'dpminplotLMA',-0.25,'dpmaxplotLMA',0.25,'caxrange',[-10 0],'caxrange_r',[-10 -5],'nogrid');
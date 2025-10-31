% autor: axelpadilla@ciencias.unam.mx (FC-UNAM)
% verion: 1.1 STP
\LoadClass[10pt, letterpaper, twoside]{article}

% Configuración de fuente
\RequirePackage{lmodern}
\RequirePackage[T1]{fontenc}
\renewcommand{\ttdefault}{lmtt}% Fuente mono
\renewcommand{\rmdefault}{lmr}% Fuente serif
\renewcommand{\sfdefault}{lmss}% Fuente sans-serif

% Diseño del documento
\RequirePackage{abstract, apptools, calc, etoolbox, fancyhdr, tabularray, titlesec, xpatch}
\RequirePackage[shortlabels, inline]{enumitem}
\RequirePackage[margin=1in, headheight=2\baselineskip, headsep=\baselineskip]{geometry}
\RequirePackage[pdfusetitle, colorlinks]{hyperref}
\RequirePackage[titles]{tocloft}
\setlength{\columnsep}{20pt}

% Gráficos
\RequirePackage{float, graphbox, graphicx, pdflscape, pdfpages, pgfplots, subcaption, tcolorbox}
\RequirePackage[font=it, labelfont=bf, format=hang]{caption}
\RequirePackage[outline]{contour}
\graphicspath{{images/}{shields/}}

% Bibliografía
\RequirePackage[backend=biber]{biblatex}
\RequirePackage[style=mexican]{csquotes}
\addbibresource{biblio.bib}

% --- Configuraciones adicionales de paquetes ---

% Versión de PGFplots
\pgfplotsset{compat=newest}

% Librerías de pgfplots
\usepgfplotslibrary{colormaps}

% Librerías de tikz
\usetikzlibrary{angles, arrows, arrows.meta, babel, backgrounds, calc, external, intersections, patterns, perspective, quotes, scopes, shadows, shapes, shapes.geometric}

% Definición de estilos de Tikz, etc.
\tikzset{
    font = {\selectfont},
	frame/.style={thin, dashed, lightgray, line cap=round, rounded corners=5pt}}
 
% Grosor de contorno adicional (para emplearse en gráficos)
\contourlength{1pt}

% Librerías de tabularray
\UseTblrLibrary{amsmath}
\UseTblrLibrary{booktabs}

% Colores
\definecolor{color1}{rgb}{0.227, 0.075, 0.267} %Violeta uno
\definecolor{color2}{RGB}{85, 37, 100} %Violeta dos
\definecolor{prussian}{RGB}{0, 50, 98} %Prussian blue
\definecolor{grisclaro}{HTML}{EAEDEF}

% Diseño de títulos de sección
\titleformat{\section}
{\centering\normalfont\Large\bfseries}{\thesection.}{1ex}{}

\titleformat{\subsection}
{\normalfont\large\bfseries}{\thesubsection.}{1ex}{}

\titleformat{\subsubsection}
{\normalsize\bfseries}{\thetitle.}{\widthof{\enspace}}{\normalsize}

\AtAppendix{\titleformat{\section}[block]
    {\centering\normalfont\Large\bfseries}{\appendixname\ \thesection.}{1ex}{}
}

% Listas personalizadas
\setlist[enumerate, 1]{
	label={\textbf{\arabic*.}},
	ref=\textbf{\arabic*}
}
\setlist[enumerate, 2]{%
	label={\textbf{(\alph*)}},
	ref=\textbf{(\alph*)}
}
\setlist[enumerate, 3]{%
	label={\roman*.},
	ref=\roman*
}

\setlist[itemize, 1]{%
	label={\textbullet},
}
\setlist[itemize, 2]{%
	label={--},
}
\setlist[itemize, 3]{%
	label={*},
}

% Redefinición de "y otros" en la bibliografía
\DefineBibliographyStrings{spanish}{andothers={et~al\adddot}}

% Tokens para llenar el documento
\newtoks\subtitle
\newtoks\subject
\newtoks\email

% Personalización del título de tablas largas con tabularray
\NewTblrTheme{replab}{
	\SetTblrStyle{caption-tag}{font=\bfseries}
	\DefTblrTemplate{caption-sep}{default}{\bfseries.\enskip}
}

% --- Página de título de documento ---
\makeatletter
\renewcommand\maketitle{

\renewcommand\thefootnote{\@fnsymbol\c@footnote}%
    	\def\@makefnmark{\rlap{\@textsuperscript{\normalfont\@thefnmark}}}%
    	\long\def\@makefntext##1{\parindent 1em\noindent
    			\hb@xt@1.8em{%
    			  \hss\@textsuperscript{\normalfont\@thefnmark}}##1}

\begin{center}
    \begin{minipage}{0.3\textwidth}
        \includegraphics[width=\textwidth]{shields/vertical.pdf}
    \end{minipage}
    \vspace{5pt}
    \begin{minipage}{0.6\textwidth}
        \begin{center}
        {\large{\textbf{\@title}} \\ \LARGE{\textbf{\the\subtitle}} \\ \medskip
    
    % --- Opción para un solo autor (predeterminada) ---
    
    	\small\@author\\
    	{\footnotesize\the\email}
    
    % --- Opción para dos autores ---
    
        %\small
        %\begin{tabular}{c@{\hspace{3em}}c}
        %    Nombre del autor 1 & Nombre del autor 2\\ 
        %    \href{mailto:emailautor1@email.com}{\footnotesize\color{prussian}\texttt{emailautor1@email.com}} & \href{mailto:emailautor2@email.com}{\footnotesize\color{prussian}\texttt{emailautor2@email.com}}
        %\end{tabular}
    
    % --- Opción para tres autores ---

        %\small
        %\begin{tabular}{c@{\hspace{3em}}c@{\hspace{3em}}c}
        %     Nombre del autor 1 & Nombre del autor 2 & Nombre del autor 3 \\ 
        %     \href{mailto:emailautor1@email.com}{\footnotesize\color{prussian}\texttt{emailautor1@email.com}} & \href{mailto:emailautor2@email.com}{\footnotesize\color{prussian}\texttt{emailautor2@email.com}} & \href{mailto:emailautor3@email.com}{\footnotesize\color{prussian}\texttt{emailautor3@email.com}}
        %\end{tabular}
    
    % --- Opción para cuatro autores ---

        %\small
        %\begin{tabular}{c@{\hspace{3em}}c}
        %     Nombre del autor 1 & Nombre del autor 2 \\ 
        %     \href{mailto:emailautor1@email.com}{\footnotesize\color{prussian}\texttt{emailautor1@email.com}} & \href{mailto:emailautor2@email.com}{\footnotesize\color{prussian}\texttt{emailautor2@email.com}} \\[10pt]
        %     Nombre del autor 3 & Nombre del autor 4 \\
        %     \href{mailto:emailautor3@email.com}{\footnotesize\color{prussian}\texttt{emailautor3@email.com}} & \href{mailto:emailautor4@email.com}{\footnotesize\color{prussian}\texttt{emailautor4@email.com}}
        %\end{tabular}
    
    	\medskip
    		
    	Facultad de Ciencias Matemáticas y Naturales\\
      
    	Universidad Distrital Francisco José de Caldas
    		
    	\medskip
    		
    	\textit{\@date\\[1ex]}}
        \end{center}
    \end{minipage}
\end{center}

\thispagestyle{plain}
}
\makeatother

% Rediseño del estilo plain

\fancypagestyle{plain}{
\renewcommand{\headrulewidth}{0pt}	
\fancyhf{}
\fancyfoot[c]{
    \begin{tblr}{c c c}
	$\boldsymbol{-}$
	& \thepage &
	$\boldsymbol{-}$
    \end{tblr}
    }
}

% Diseño de los encabezados y pies de página
\fancypagestyle{fancy}{
    \fancyhf{}
    \fancyhead[le]{
        \begin{tblr}{
            colspec = {Q[c,m] Q[l,m]},
            colsep = 2pt
		}
        \includegraphics[
		align=c,
		width=2.5ex]{shield}
    	& {\small{Facultad de Ciencias Matemáticas y Naturales}}
        \end{tblr}
    }
    \fancyhead[re]{
        \small\textit{\the\subject}
    }
    
    \fancyhead[co]{
        \begin{tblr}{c}
            \small\textit{\the\subtitle}
        \end{tblr}
    }
    
    \fancyfoot[c]{
        \begin{tblr}{c c c}
    	{$\boldsymbol{-}$}
    	& \thepage &
    	{$\boldsymbol{-}$}
        \end{tblr}
    }
}

% --- Comandos de mate adicionales ---

\newcommand{\pqty}[1]{%
    \left( #1 \right)
}

\newcommand{\bqty}[1]{%
    \left[ #1 \right]
}

\newcommand{\Bqty}[1]{%
    \left\lbrace #1 \right\rbrace
}

\newcommand{\abs}[1]{%
    \left\lvert #1 \right\rvert
}

\newcommand{\norm}[1]{%
    \left\lvert\left\lvert #1 \right\rvert\right\rvert
}

\newcommand{\rtwovec}[2]{% Vectores columna en R^2 
	\begin{bmatrix*}[r]
		#1 \\ #2 
	\end{bmatrix*}
}

\newcommand{\rthreevec}[3]{% Vectores columna en R^3
	\begin{bmatrix*}[r]
		#1 \\ #2 \\ #3
	\end{bmatrix*}
}

\newcommand{\bvec}[1]{% Vectores
	\mathbf{#1}
}

\newcommand{\uvec}[1]{% Vectores unitarios (con gorrito)
	\textbf{\^{#1}}
}

\newenvironment{amatrix}[2]{% Matices aumentadas
	\left[\begin{array}{@{}*{#1}{r}|*{#2}{r}@{}}
	}
	{
	\end{array}\right]
}
# Schedule

- Hands-on  
- pip install pre-built wheel, then link custom dialect (that participants write during exercises). same infrastructure shared for all sessions.  
- experienced \+ beginner audience

Theme ideas:

* Scalable vectors  
* Transform dialect  
* Interfaces  
* CUDA TileIR  
  * Can rent GPU to run on  
* mem2reg  
* Dataflow analysis  
  * forwards/backwards  
* Bounds analysis  
* Bufferization  
* Rewrites  
* Symbols  
* PDL  
* Eqsat in MLIR  
* Python bindings  
* Assembly dialects  
* SMT dialect  
* Lowering to LLVM  
* Deep dive in IR data structure  
* Deep dive in TblGen

- Structured Control Flow  
- Parser/Printer (Can be part of ODS)

Unifying problem ideas:

- Digital signal processing (the modeling of f32 over time)

Links:

- [https://github.com/DavidGinten/ML-compiler-exercise/tree/main](https://github.com/DavidGinten/ML-compiler-exercise/tree/main)

## 

## Schedule: First track

1. Compiler basics: (SADAY, TOBIAS)  
   1. SSA IR, etc.  
   2. What is a pass  
   3.   
2. Introduction of running example / topic. What IR are we going to use throughout the remaining sessions? TODO: Topic? DSP? Complex numbers? Something else? (THEO)  
   1. Introduction to MLIR.  
   2. Operations / IR Structure / Regions  
   3. How to represent (2) in IR. How do you design IR in MLIR?  
3. Pass infrastructure: implement your first MLIR pass. (MATTHIAS)  
4. Pattern infrastructure (incl. PatternRewriter, Builder API) (MATTHIAS)  
5. Interfaces (MATTHIAS)  
6. Core transformations: Canonicalization / folding / CSE / TrivialDCE pass / etc (MARKUS)   
7. Data flow analysis (MATHIEU)  
8. Mem2Reg (THEO)  
9. Deep dive in TblGen \+ ODS (MARKUS)  
10. Deep dive in IR datastructure / performance (MATHIEU)  
11. GPU CUDA Tile IR (THEO)

# Introduction

# Introduction Session

*Lead: Kunwar & Tobias*

# Compiler Introduction

# Compiler Introduction

*Lead: Tobias & Saday*

# MLIR IR Introduction

# MLIR IR Introduction

*Lead: Theo*

High-level Plan/Goals:

* No C++ in this session.  
* Very interactive, basically only exercises

Plan:

# Poster Session

# Poster Session

*Owner: ?*

# Building Transformations

# Building Transformations

*Lead: Matthias*

# Core Transformations

# Core Transformations

*Lead: Matthias*

# ODS

# ODS

*Lead: Markus*

Overall Goals:

* Defining dialects, C++ APIs

# Interfaces

# Interfaces

*Owner: Mathias*

# Mem2Reg

# Mem2Reg

*Owner: Théo*

# Data Flow Analysis

# Data Flow Analysis

*Owner: Mathieu*

# IR Data Structures and Performance

# IR Data Structures and Performance

Owner: Mathieu

# CUDA Tile IR

# CUDA Tile IR

*Owner: ?*

# Transform Dialect

# Transform Dialect

Owner: Max

# Solar Eclipse

# Solar Eclipse

*Owner: Gabriel*

# Meeting Notes

### 2026-06-16

* Attendees  
  * Matthias, Kunwar, Theo, Mathieu, Max Bartel, Sasha, Jules, Tobias, Gabriel  
* Topics  
  * First/Second track  
    * Theo: should the second track be used for people who need more time for the first track?  
      * Let’s discuss this later, first making schedules/courses for first/second track then see how they’ll interact  
    * Sessions are 10-14 and 16-20  
      * Wednesday is a half-day  
      * Monday afternoon will have posters  
        * Have morning session  
        * Afternoon or half afternoon for posters?  
          * If half then better to do last half of session, 6-8pm  
  * [Introduction session]()  
    * Lead: Kunwar, Support: Tobias  
    * Will discuss offline how to organize  
  * School got accepted by ACM  
    * Requirements:  
      * They come and talk about ACM  
      * Sessions will be recorded and hosted by ACM  
  * We already have glasses for the eclipse  
  * Some sessions that we initially proposed did not fit into the schedule  
    * Tobias warns against scheduling too many things, proposed work already quite a lot  
    * Better to first make sure that the core sessions are ready (within 2-3 weeks)  
    * Feedback from 2025 Summer School was that introductory sessions first would be good  
      * Move Mem2Reg to Thursday and Analysis to Wednesday?

### 

### 2026-05-22

* Attendees  
  * Matthias, Markus, Teho, Kunwar, Maximilian, Gabriel, Sasha, Mathieu  
* Topics  
  * Two rooms \-\> Two tracks \- fast and slow  
    * Schedule TBD  
    * How do people know which track to attend?  
      * Not clear right now  
      * Maybe just do one track and do hacking in the second room?  
  * Jules to teach PDL?  
    * He has applied to join, which makes it easier to make him a teacher also, other teachers already confirmed  
  * Schedule  
    * See Schedule tab  
    * Max shared [ML compiler exercises](https://github.com/DavidGinten/ML-compiler-exercise/tree/main) made by an intern at Roofline  
    * Topics:  
      * Max   
        * Scalable vectors  
        * Transform dialect  
        * Interfaces  
      * Theo   
        * TileIR  
          * Can rent GPU to run on  
        * mem2reg  
      * Matthias  
        * Dataflow analysis  
          * forwards/backwards  
        * Bufferization  
        * Rewrites  
      * Mathieu  
        * Symbols  
      * Sasha  
        * PDL  
        * Eqsat in MLIR  
        * Python bindings  
        * Assembly dialects  
      * Kunwar  
        * SMT dialect  
          * Better for expert track  
      * Markus  
        * MLIR C++ datastructures  
          * How does SSA actually look like in C++?  
        * Lowering to LLVM  
          * Intro to LLVM from the perspective of an MLIR user  
        * Tablegen deep dive  
          * Tablegen the language & ODS  
          * Maybe as part of dialect definition?  
      * Kunwar suggested adding more themes directly to the schedule tab for now offline  
    * Ordering:  
      * Defining your own IR vs existing IRs  
        * Sasha suggested using existing IRs first, then defining own, Kunwar suggested the other  
        * How to design an IR probably the most valuable thing to teach  
        * Can decide on the order later  
  * Overall Structure  
    * Want the exercises to be uniform  
    * At PPoPP in Sydney distributing MLIR wheels built for four architectures worked consistently including on old laptops  
    * Can include xDSL notebooks but Kunwar’s objective is to have uniform exercises  
      * Some notebooks don’t show any Python APIs, these could still be useful to explain MLIR functionality, will need to see WRT schedule  
  * Meta  
    * Will meet weekly for the first few weeks then potentially keep the slot but meet less regularly  
    * First priority is to decide on overall structure then can divide tasks

Two Track Discussion:

- Don’t name them beginner/advanced, rather name them foundation/something-else  
- A good idea is to have more explanations for “why some MLIR internals are built this way” in the non-foundational path  
- Maybe have “expert boxes” in the lectures  
- Have some facilitators in the room to help out, which also helps with getting people talking, etc.

# Timeline

Morning: 10am \- 2pm  
Evening: 4pm \- 8pm

Monday:   
Morning:   
  Session 1: Introduction, Interactive session (Goal: Try to get people to have technical conversations with at least half of the people in the room) (KUNWAR & TOBIAS)  
  Session 2: Compiler Introduction (SADAY, TOBIAS)

Evening:   
   Session 3: Introduction to MLIR / IR, running example (THEO)  
   Poster Session (6pm \- 8pm) 

Tuesday:  
            Morning:   
               Session 4: MLIR ODS (Including defining dialect, operations) (MARKUS)  
               Session 5: Transformations: Pass Infrastructure \+ C++ API for modifying IR (MATHIAS)

            Evening:  
               Session 6: Transformations: Rewriter, Pattern Driver Infrastructure (MATHIAS)  
               Session 7: Core Transformations: Canonicalizations, CSE, DCE, folding (MARKUS)

Wednesday:  
            Morning:  
                Session 8: Interfaces \+ Traits (MATHIAS)  
                Session 9: Mem2Reg (THEO)

            Evening:  
               Possible 4pm-5pm slot available  
               After 6pm: Solar Eclipse

Thursday:   
            Morning:  
               Session 10: Data Flow Analysis (MATHIEU)  
               Session 11: IR Data Structures and Performance (MATHIEU)

             Evening:  
               Session 12: CUDA TILE IR (THEO)  
               Session 13: Transform Dialect, Tensor Compiler (MAX)

Friday: Morning: (1 session)  
           2 hours for lectures  
           2 hours for presentations

Space for total of 14 sessions of (1.5h to 1h 45min each) per track

| Monday |  |  |
| ----- | :---- | :---- |
|  | Track 1 | Track 2 |
| 10:00 \- 11:45 | [Introduction]() |  |
| 12:15 \- 14:00 | [Compiler Introduction]() |  |
| 14:00 \- 16:00 | Break | Break |
| 16:00 \- 18:00 | [MLIR IR Introduction]() |  |
| 18:00 \- 20:00 | [Poster Session]() |  |

| Tuesday |  |  |
| ----- | :---- | :---- |
|  | Track 1 | Track 2 |
| 10:00 \- 12:00 | [ODS]() |  |
| 12:00 \- 14:00 | [Building Transformations 1]() |  |
| 14:00 \- 16:00 | Break | Break |
| 16:00 \- 18:00 | [Building Transformations 2]() |  |
| 18:00 \- 20:00 | [Core Transformations]()  |  |

| Wednesday |  |  |
| ----- | :---- | :---- |
|  | Track 1 | Track 2 |
| 10:00 \- 12:00 | [Interfaces]() |  |
| 12:00 \- 14:00 | [Mem2Reg]() |  |
| 14:00 \- 16:00 | Break | Break |
| 16:00 \- 20:00 | [Solar Eclipse]() |  |

| Thursday |  |  |
| ----- | :---- | :---- |
|  | Track 1 | Track 2 |
| 10:00 \- 12:00 | [Data Flow Analysis]() |  |
| 12:00 \- 14:00 | [IR Data Structures and Performance]() |  |
| 14:00 \- 16:00 | Break | Break |
| 16:00 \- 18:00 | [CUDA Tile IR]() |  |
| 18:00 \- 20:00 | [Transform Dialect]() |  |

| Friday |  |  |
| ----- | :---- | :---- |
|  | Track 1 | Track 2 |
| 10:00 \- 12:00 |  |  |
| 12:00 \- 14:00 | Presentations |  |
| 14:00 \- 16:00 | End | End |


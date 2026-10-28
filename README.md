# Siuyu Lightbox Still Life

[简体中文](README.zh-CN.md) | [English](README.md)

**Shape materials, silhouettes and negative space in a continuous field of soft light.**

A Codex skill for reference-driven lightbox still lifes, soft-lit material arrangements and physical editorial compositions, with a companion guide for ChatGPT. Begin with what the viewer should discover, then choose the object, study medium, composition, material and light together. Generate and inspect the actual result.

Open tabletop briefs choose a study medium for the question: engraved transparent overlays, stitched samples, incised wood, wax impressions, technical diagrams or digital imagery can each change the composition and lighting. A simple lightbox request uses **transmitted light from below**, a milky luminous table and readable opaque surfaces. Paper-layer studies inspect overlap density and covered lines. Complete still lifes keep the required objects and boundaries comfortably inside the frame. See [visual language](references/visual-language.md), [study artifacts](references/study-artifacts.md) and [material processes](references/material-process-atlas.md); these detailed guides are in Chinese.

You can also request editorial print compositions: real objects with paper reproductions, halftone photographs, or graphics printed directly onto cloth. Choose the print process, color separation, carrier material and carrier color independently; the requested aspect ratio still governs the image. See the [print workflow](references/print-direction.md) and [optional local print tools](modules/print/README.md).

Codex invocation: `$siuyu-lightbox-still-life` · Author: siuyu · Version: `1.3.0-rc.5`

[Install in Codex](#codex-installation) · [Use in Codex](#codex-usage) · [Codex CLI](#codex-cli-usage) · [ChatGPT web](#chatgpt-web-usage) · [Full gallery](references/example-gallery.md) · [Interactive showcase](https://masiuyu.github.io/siuyu-lightbox-still-life/)

Version rc.5 coordinates the material observation, camera viewpoint, prop placement, diffused light field and focus in one shot. It adds portable directions for a complete product view, a material close-up and an overhead glass study; their image results are evaluated after execution.

![Scissors and tracing paper illuminated from below](assets/showcase/transmitted-paper.png)

*Light passes through the tracing paper from below. The overlapping sheets are darker, the covered pencil lines are paler, and the scissors retain readable metallic reflections. See [image details (Chinese)](ASSET_SOURCES.md).*

<a id="选择使用方式"></a>

## Choose how to use it

| Software or environment | Getting started | Guide |
|---|---|---|
| Codex desktop app or IDE extension | Install the skill and invoke it in a Codex conversation | [Installation](#codex-installation) and [examples](#codex-usage) |
| Codex CLI | Install the skill, then start `codex` in a terminal | [Codex CLI usage](#codex-cli-usage) |
| Regular Chat in ChatGPT on the web | Share the guide link and reference images in the conversation | [ChatGPT web usage](#chatgpt-web-usage) |
| Local scripts or the companion renderer | Run the relevant program to compile directions, check records, or operate the renderer | [Command-line guide](CLI.md) |

<a id="codex-安装"></a>

## What you can create

Build a series through a controlled light field, silhouettes or material windows, material differences and purposeful spatial density. Subject, color, viewpoint, material state and composition can change with each brief. See [soft-lit material staging](references/lightstage-language.md), in Chinese.

| Direction | Relationships that form the image | Current evidence |
|---|---|---|
| Light-table research still lifes | Luminous table, physical objects and study media | Nine landscape/portrait studies and the transmitted-paper showcase |
| Sculptural material arrangements | Bright diffused backgrounds, coils, drapes, stacks and support | Written guidance and directions; new images await execution |
| Product and mixed-material imagery | Broad soft light, reflected light/dark shapes and negative space | Existing metal and glass studies; [buckle lightstage direction](assets/lightstage-material-hero.example.md) awaits an image |
| Graphic and print studies | Paper, cloth, film or screens carrying painting, print and structural imagery | Directions and tools, with review of each actual image |
| Process and object-led storytelling | Material states, making sequences, hands and tool contact | Existing workbench examples; new subjects retain the chosen series relationships |

A softbox can provide broad reflections on the object, while a luminous table or diffused backdrop shapes the whole composition. Choose overhead or side views for the observation needed. Review both the task result and the shared visual relationships before selecting series images.

Product views connect material, camera, props and light. Choose the thickness, liquid level, connection or reflection to read, then arrange viewpoint, depth, background gradient and focus. Transparent objects distinguish background color, internal transmission and surface highlights. Three new written directions cover a [complete hero](assets/optical-product-hero.example.md), [material close-up](assets/optical-product-macro.example.md) and [overhead material grouping](assets/optical-material-overhead.example.md). They compile; their actual images await execution. See [product-view coordination](references/photography.md#产品镜头把材料位置与光一起确定), in Chinese.

The [full gallery](references/example-gallery.md) retains native images and execution records. [Task exploration records](references/example-gallery.md#task-exploration-records) document separate material close-up, narrative photography and watercolor results. Explicit requests for standalone media are created and reviewed against their own brief.

## Codex installation

For the Codex desktop app, CLI, or IDE extension with access to local files. Choose one of the following methods. If you are new to Codex CLI, start with the [official Codex CLI setup guide](https://learn.chatgpt.com/docs/codex/cli).

<a id="在-codex-对话中安装"></a>

### Install from a Codex conversation

Send this request to Codex:

```text
Install this skill from
https://github.com/masiuyu/siuyu-lightbox-still-life.
Read the repository instructions and run the package validator, then install
the complete skill in ~/.agents/skills/siuyu-lightbox-still-life.
If a version with the same name already exists, back it up in full first.
Check that Codex can discover the skill, and report its actual installation
path and invocation.
```

After installation, start a new Codex conversation and use `$siuyu-lightbox-still-life`. If it has not appeared, restart Codex. See [installation locations and updates](#codex-installation-locations-and-updates) for user and project directories.

<a id="用终端安装到当前项目"></a>

### Install into the current project from a terminal

With Node.js and npm installed, open a terminal in the project where you want to use the skill:

```bash
npx skills add https://github.com/masiuyu/siuyu-lightbox-still-life --skill siuyu-lightbox-still-life --agent codex
```

This uses the third-party [skills installer](https://github.com/vercel-labs/skills). The `--agent codex` flag selects Codex, and the project installation is available through `.agents/skills/`. Open Codex in that project after installation.

For a ZIP download or installation into your user directory with Python, see [other Codex installation methods](#other-codex-installation-methods).

<a id="codex-使用"></a>

Current guidance connects where content exists, how it becomes an image, and the chosen carrier before resolving material, light and camera. Local edits use one base image and explicit reference roles; direction, source size, intensity, light color and white balance are separate decisions. See [execution](references/prompt-execution.md), [materials](references/material-color.md) and [lighting](references/lighting-optics.md). Each task records method checks and actual image evidence separately.

The [composite material cases](references/material-construction-cases.md) connect substrates, coatings, machining direction, angle color and thin-wall transmission to concrete design and observation choices. Wood, metal components, a thin-film clip, a lampshade, glaze, fibers and print each use suitable shape, light and framing. These directions support new tasks; image effects are assessed from actual generated results.

By default, [visual hierarchy and Smooth Control](references/visual-hierarchy-smooth-control.md) establish one primary visual goal, followed by composition, key light-color-material relationships and necessary detail. Keep large transitions, tonal areas and space clear while preserving photographic skin, materials, contact and environment. Macro studies, specified styles and local edits follow their actual scope. The compiler transports the authored direction verbatim.

[Viewing purpose and image formation](references/restaged-print-world-editorial.md) connect decisions across a task. Surface comparison calls for useful lit areas; structural explanation calls for readable connections and projection; a scene calls for actions, distances and a coherent space. Choose color, density and medium for that purpose. Portable directions cover material, structural and standalone media tasks. Existing images retain reviews of their respective goals; series selection additionally checks the chosen light field, silhouettes, space and material relationships. [Method sources and contributions](references/method-sources.md) record specific research influences and usage scope.

## Codex usage

Send these requests in a Codex conversation where the skill is loaded. `$siuyu-lightbox-still-life` invokes the skill; attach your reference photographs to the conversation.

If you have a specific object:

```text
Use $siuyu-lightbox-still-life to create a 16:9 light-table still life from
the attached images.
Photograph it directly from above. Preserve the subject's actual structure
and arrange a matching contour drawing and material samples nearby.
Lay the tracing paper on a luminous table, with light passing upward through
it and clear tonal differences at the overlaps.
Let the table fill every edge of the image. Keep the subject and drawings
completely in frame, with space between objects.
Generate the image, then open it and inspect the result.
```

If you are starting from an idea:

```text
Use $siuyu-lightbox-still-life to design a 9:16 material study of a glass
cup.
Make the opening, walls, base, and handle clearly readable.
Arrange a contour drawing, glass samples, and translucent paper layers
beside the cup to reveal its structure and the way light passes through the
glass.
```

<a id="codex-cli-使用"></a>

## Codex CLI usage

Install the skill first. Open a terminal in the directory where you want to save the work, then run:

```bash
codex
```

Enter `/skills` in the Codex interface to check the loaded skills, then send one of the [usage examples](#codex-usage). For starting with an image, passing a request on the command line, and using local scripts, see the [CLI guide](CLI.md#codex-cli).

<a id="五种画面方向"></a>

## Choose a direction for the viewing task

| Direction | Visual emphasis |
|---|---|
| **Transmitted light (lightbox baseline)** | A bright milky table lights paper and translucent sheets from below. Overlaps become darker, covered sketch lines become paler, and opaque objects retain reflections and dark tones. |
| Soft paper layers | Tracing paper on a milky surface, with subtle texture and lower drawings visible through the upper sheets. |
| Color-field hero image | A broad field of color supports the subject, such as a blue-gray surface framing the shape and shading of a white porcelain cup. |
| Workbench action | Drawing, arranging, or holding a sheet, with credible contact between hands, tools, and objects. |
| Material close-up | Reflections, brushed metal, paper fibers, or another selected detail, framed at a useful scale. |

These are starting points. For open exploration, choose a viewing idea and study medium, then resolve material construction, space and light. A consistent series preserves its selected relationships; exploratory directions compare concrete changes in form, medium, composition and light. Compose each format separately.

<a id="横幅与竖幅分别构图"></a>

## Compose separately for landscape and portrait

| Landscape · 16:9 | Portrait · 9:16 |
|---|---|
| ![Coffee spoon study in landscape](assets/examples/real-objects-20260913/02-spoon-paper/landscape/image.png) | ![Coffee spoon study in portrait](assets/examples/real-objects-20260913/02-spoon-paper/portrait/image.png) |

Each format has its own arrangement of the subject, drawings, and paper layers. A pair can share objects, materials, and color while adapting its grouping and spacing to each frame.

<a id="随包提供的案例"></a>

## Included examples

These existing lightbox images document their own tasks. The added medium methods require their own authorized images and visual reviews.

The original lightbox gallery contains nine subjects and studies, each with a landscape and portrait image: eighteen images. The transmitted-paper image and three new cross-subject examples bring the package to twenty-two independent images. Open the [full gallery](references/example-gallery.md) to compare the compositions and inspect each image's original generation and review records.

| Example | What to look for |
|---|---|
| [Glass cup transmission study](references/example-gallery.md#example-01) | Connections between the rim, base, and handle, and the transmission of overlapping glass samples. |
| [Coffee spoon contour and paper layers](references/example-gallery.md#example-02) | Correspondence between the physical spoon and its graphite drawing. |
| [Porcelain cup color-field hero](references/example-gallery.md#example-03) | A blue-gray surface supporting the form and shading of a white cup and saucer. |
| [Drawing a coffee spoon](references/example-gallery.md#example-04) | One hand steadies the paper while the other holds a pencil, with readable contact points. |
| [Coffee spoon surface detail](references/example-gallery.md#example-05) | Polished reflections in the bowl and brushed texture along the handle. |
| [Coffee spoon finish comparison](references/example-gallery.md#example-06) | Polished steel, brushed steel, and graphite hatching as related surface studies. |
| [Holding a coffee spoon drawing](references/example-gallery.md#example-07) | Supported paper curvature and the difference between exposed and covered drawing lines. |
| [Embossed letter on cotton paper](references/example-gallery.md#example-08) | Shallow embossing, paper fibers, and cut edges. |
| [Translucent paper on a lightbox](references/example-gallery.md#example-09) | Single and overlapping paper densities, with a pencil line continuing across an overlay boundary. |

<a id="它怎样工作"></a>

## Natural-language workflow

Describe the subject, format, preservation requirements and visible result. The AI views the actual sources and writes direction.md as complete prose about image uses, object relationships, construction, materials and light.

The reference-images section lists local images in order; the image-instructions section contains the exact prompt. Observations and selection notes stay in other sections. `lightbox.py compile` transports that prompt and order, `check` verifies the saved bundle, and `review` summarizes actual observations. Compilation, image generation, visual review and user acceptance retain separate evidence. See [execution](references/prompt-execution.md) and [migration](references/interface-migration.md).

## How it works

1. **Identify the subject and the role of each reference.** Inspect the attachments to establish the object's parts and shape, and what each reference contributes. For a written idea, define the object and its structure first.
2. **Design and generate the image.** Arrange the lighting, materials, and objects, assemble a complete prompt, and use the image tool available in the current environment. The full Codex workflow saves the direction and compiles an image job through a script.
3. **Open and inspect the result.** Check identity, structure, paper transmission, and composition, then examine physical contact and any interaction between hands, tools, and objects. Refine specific issues when needed.

The usual Codex delivery includes the image, authored direction, actual image job, and a short visual review. The web workflow provides images, prompts, and relevant notes according to the conversation's available tools; see the [ChatGPT guide](CHATGPT.md).

<a id="codex-常用请求"></a>

## More Codex requests

Send these examples to Codex. Copyable requests for regular ChatGPT Chat are in the [web section](#chatgpt-web-usage).

**Preserve a product's shape and materials:**

```text
Use $siuyu-lightbox-still-life to turn the attached product into a
light-table material study.
Preserve its actual structure and colors. Match the drawing to the product's
contour,
and choose material samples that relate to its surfaces.
```

**Create a landscape and portrait pair:**

```text
Use $siuyu-lightbox-still-life to create one 16:9 image and one 9:16 image
of the same subject.
Keep the materials and colors consistent, and arrange the objects, paper
layers, and surrounding space for each format.
```

**Refine the transmission in an existing image:**

```text
Use $siuyu-lightbox-still-life to continue editing this version.
Keep the subject and drawing in place, and strengthen the light passing
through the tracing paper from below.
The overlap should be darker than a single sheet, and the covered pencil
lines should be paler.
Inspect the edited image and check both relationships.
```

<a id="chatgpt-网页版使用"></a>

## ChatGPT web usage

Open [ChatGPT](https://chatgpt.com/), start a regular **Chat** conversation, and attach your reference images. Share this request so the model can read the creative guide and apply it in the current conversation:

```text
Read the Siuyu Lightbox Still Life guide for ChatGPT:
https://github.com/masiuyu/siuyu-lightbox-still-life/blob/main/CHATGPT.md

Follow the guide to create a 16:9 light-table still life from my
attachments.
Preserve the subject's structure and arrange a matching design drawing on
complete rectangular tracing paper.
Show light passing upward through single and overlapping sheets. Keep the
subject, tools, and all paper edges fully in frame, with natural spacing.
Generate the image and continue refining it with my feedback.
```

Replace the subject, format, and visual requirements with your own. See the [ChatGPT guide](CHATGPT.md) for the complete workflow and more examples.

<a id="链接读取与图片生成"></a>

### Reading links and generating images

- **If the link cannot be read:** Open [CHATGPT.md](CHATGPT.md), paste its full text into the conversation or upload the downloaded file, then send your request.
- **If the conversation only supports text:** Ask for a complete prompt to use with your chosen image tool. To generate within ChatGPT, use a conversation with image generation available. Availability depends on the plan and workspace settings; see the [ChatGPT image guide](https://learn.chatgpt.com/docs/image-generation).
- **Usage limits:** Regular Chat follows the account's current messaging and image limits. ChatGPT Work and Codex share usage limits; see [OpenAI's usage guide](https://learn.chatgpt.com/docs/pricing).

<a id="运行环境"></a>

## Requirements

The skill supplies the creative workflow and supporting scripts. The host software provides file access, image viewing, and image generation.

| Workflow | Requirements |
|---|---|
| Full workflow in Codex desktop, CLI, or IDE extension | Skill loading, local file access, and image viewing; Python 3.10 or newer; an available image tool for generation |
| Installation with `npx skills` | A terminal, Node.js, and npm; select Codex in the installation command |
| Repository Python scripts | Local Python 3.10 or newer; direction and review commands use the standard library. Image evidence commands also need Pillow. See [script inputs and outputs](CLI.md#python-scripts). |
| Regular ChatGPT Chat on the web | Access to the guide through a link, pasted text, or an uploaded document; image generation must be available to produce images |
| Companion local renderer | A separately prepared renderer project with Node.js, pnpm, and its dependencies; see [renderer CLI](CLI.md#renderer-cli) |

The complete image workflow has been used and checked in the Codex desktop environment. Other clients depend on their available tools. To adapt it to another agent, configure that agent's skill directory, attachments, script execution, and image tool interface.

<a id="codex-其他安装方式"></a>

## Other Codex installation methods

Run these commands in a macOS, Linux, or Windows WSL terminal. They install the skill in a user directory discoverable by Codex, for use across local projects.

<a id="从-github-克隆后安装"></a>

### Clone from GitHub and install

Requires Git and Python 3.10 or newer:

```bash
git clone https://github.com/masiuyu/siuyu-lightbox-still-life.git
cd siuyu-lightbox-still-life
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills"
```

<a id="从-zip-安装"></a>

### Install from a ZIP

Download and extract the repository ZIP. Open a terminal in the directory containing `SKILL.md`, then run:

```bash
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills"
```

<a id="codex-安装位置与更新"></a>

### Codex installation locations and updates

The user installation above goes into `~/.agents/skills/siuyu-lightbox-still-life`. A project installation lives in that project's `.agents/skills/siuyu-lightbox-still-life`. See the [official Codex skills guide](https://learn.chatgpt.com/docs/build-skills) for directory conventions.

To update an installation made with this repository's Python script, get the latest repository files, then run from its root:

```bash
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills" --backup-existing
```

The complete previous version is saved in `skill-backups/` beside the target skills directory, and the script reports the actual location. For a custom installation, set `--target-root` to the parent of your skill directory. Manage installations made with the third-party `skills` tool through that tool's update process.

When `--target-root` is omitted, the Python script uses `$CODEX_HOME/skills`, or `~/.codex/skills` if the environment variable is unset. The commands above select the directory explicitly to follow the current Codex local skills convention. Start a new conversation after installation; restart Codex if the skill has not appeared.

<a id="按用途查阅文档"></a>

## Documentation

| Document | Audience |
|---|---|
| [Codex installation and usage](#codex-installation) | Codex desktop, CLI, and IDE extension users |
| [Command-line guide](CLI.md) | Codex CLI, installer, Python script, and companion renderer users |
| [ChatGPT guide](CHATGPT.md) | Web users sharing the guide through a link, pasted text, or an upload |
| [Agent instructions (Chinese)](SKILL.md) | Codex and agents adapting the complete workflow |
| [Direction compilation and image invocation (Chinese)](references/prompt-execution.md) | Operators preparing direction files, image jobs, and generation records |
| [Local renderer workflow (Chinese)](references/offline-workflow.md) | Developers with a renderer project who need deterministic output or source-layer composition |
| [Local renderer development (Chinese)](references/codex-execution.md) | Developers installing or integrating the companion renderer |
| [Example gallery](references/example-gallery.md) | Readers exploring composition and material rendering |

<a id="包内结构"></a>

## Package layout

```text
siuyu-lightbox-still-life/
├── SKILL.md                 # Agent instructions, in Chinese
├── README.md                # English introduction and installation
├── README.zh-CN.md          # Chinese introduction and installation
├── CLI.md                   # English command-line guide
├── CLI.zh-CN.md             # Chinese command-line guide
├── CHATGPT.md               # English guide for regular ChatGPT Chat
├── CHATGPT.zh-CN.md          # Chinese guide for regular ChatGPT Chat
├── ASSET_SOURCES.md         # Image information, in Chinese
├── agents/openai.yaml       # Name, icons, and default invocation
├── assets/                  # Configurations, presets, and generated images
├── references/              # English and Chinese galleries; detailed guidance
├── scripts/                 # Installation, compilation, and checks
└── evals/                   # Behavioral evaluation scenarios
```

<a id="常见问题"></a>

## Frequently asked questions

**Do I need a photograph?** Attach a photo when you want to preserve a particular object's appearance. For a new design, start with a written idea. With multiple references, identify which establish structure and which guide lighting, color, or composition.

**Can I specify an aspect ratio or pixel dimensions?** The defaults are 16:9 landscape and 9:16 portrait; other ratios and target dimensions are supported as requests. The actual output depends on the image tool and is recorded on delivery. Included examples are natively 1672×941 or 941×1672, with a small rounding difference from the target ratios.

**Will every image use the same arrangement?** Presets guide lighting and materials. Objects, drawings, and layout are designed for your request. When editing an existing image, specify which positions, colors, or materials to preserve.

**Can I download the examples?** Yes. All twenty-two independent generated images are included under `assets/` and are available when you clone the repository or download its ZIP. See [image information (Chinese)](ASSET_SOURCES.md).

<a id="配图与发布信息"></a>

## Images and release information

The twenty-two independent images in this package were generated with an AI image tool. Nine landscape/portrait pairs, transmitted paper and three new examples explore objects, materials, human relationships and painting. Web previews are format exports of corresponding images. See [image details (Chinese)](ASSET_SOURCES.md) for their generation information. The current version is `1.3.0-rc.5`.

## Developing form and material comparisons

Choose what the viewer should recognize or compare, then describe concrete operations such as unfolding, perforation, bending, layering or ink separation. Keep subject relationships across a series while recomposing each aspect ratio. Assign overall identity and microscopic surface evidence to appropriate views. See the Chinese [design guide](references/design-development.md), [six case studies](references/case-derived-lessons.md) and [opening study](assets/opening-study.example.md). These methods have been applied to directions; new image results require their own tests.

The [ink-layer study](assets/ink-layer-study.example.md) tests a separate ink line over a continuous base coat before transferring the material construction to a target graphic. It is a prepared direction awaiting its image test.

## Material, lighting and style across subjects

The Chinese [material guide](references/material-color.md) separates color coverage, reflection, texture scale and physical shape, with examples for metal, ceramic, glass, wood, cloth and paper. The [lighting guide](references/lighting-optics.md) assigns visible jobs to light and checks their interactions. The [style transfer guide](references/style-transfer.md) preserves subject identity while adapting visual relationships to new materials and formats. Prepared [ceramic](assets/ceramic-surface-study.example.md) and [glass](assets/glass-volume-study.example.md) directions demonstrate the method; their image results remain to be tested.

## Creative relationships and focused routing

The Chinese [creative judgment guide](references/creative-judgment.md) applies existing expertise to the current decision: choose an idea that organizes the image, resolve tradeoffs, state a critical expected observation, then use the actual result to choose the next action. Deepen established directions while preserving the user's accepted scope.

The Chinese [creative workflow](references/creative-orchestration.md) connects the task, subject, visual idea, form, material, light and viewpoint, then routes visible failures to the relevant decision. Use only the modules needed for the current task. [Art direction](references/image-art-direction.md) develops visual weight, color fields, negative space and further discovery. [Prompt patterns](references/prompt-patterns.md) express selected decisions; [camera and motion](references/camera-and-motion.md) distinguishes viewpoint, framing, object and lighting changes.

Prepared [glass hero](assets/open-form-hero.example.md) and [two-color artwork](assets/open-form-artprint.example.md) directions explore the same basic form through different media. Their image effects await actual generation; temporal effects need their own sequence evidence.

## From light to the delivered image

The Chinese [image development guide](references/image-development.md) connects the scene to exposure, color treatment and final viewing, including emissive products and protected reading areas. [Material guidance](references/material-color.md) follows texture directions over local surfaces; [camera guidance](references/camera-and-motion.md) separates stable scene relationships from each view’s projection. The [workflow](references/creative-orchestration.md) identifies which decisions need another check after a material, light, camera, crop, medium or grading change. These methods are integrated; visual improvements require actual outputs.

## Saved images, calls and reviews

The optional [image evidence workflow](references/image-evidence.md) binds a compiled job, saved imagegen arguments, a native still and its review. It can compare indexed crops pixel for pixel with their native source, then recheck file changes against the saved record. These commands require Pillow; ordinary direction compilation and review retain their existing interface. Visual quality and user acceptance continue to rely on their own evidence.

## Scale and viewing conditions

[Framing](references/camera-framing.md) combines the bounds of rotated objects and distinguishes physical size, frame coverage and detail pixels. Recheck material cues and light coverage after widening the view. [Model construction](references/model-construction.md) translates recognition features into the chosen fabrication language; [materials](references/material-color.md) connects color, reflection and relief through compatible causes and corresponding samples. [Camera and motion](references/camera-and-motion.md) checks coverage during movement, newly revealed surfaces and final playback. These methods are integrated locally; new image and video effects require actual outputs.

For repeated calculations, the optional [framing preflight](references/framing-preflight.md) command, `lightbox.py framing`, estimates rotated rectangle bounds, margins and detail pixels from declared dimensions or design assumptions. It evaluates the plan; directions and image execution keep their natural-language interface.

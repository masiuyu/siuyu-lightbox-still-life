<a id="在-chatgpt-网页-chat-中使用-siuyu-lightbox-still-life"></a>

# Use Siuyu Lightbox Still Life in ChatGPT on the web

[简体中文](CHATGPT.zh-CN.md) | [English](CHATGPT.md)

Read, paste, or upload this guide into a regular Chat conversation in ChatGPT. It describes a light-table still-life workflow that can be followed directly in the conversation. The user's current request and the attachments actually available to the model establish the creative brief.

For a local installation, see [Codex installation](README.md#codex-installation). For terminal use, see the [Codex CLI guide](CLI.md#codex-cli).

<a id="开始使用"></a>

## Get started

Start a regular Chat conversation in ChatGPT, attach photographs or describe your idea, and send:

```text
Read
https://github.com/masiuyu/siuyu-lightbox-still-life/blob/main/CHATGPT.md
and follow this guide to work with my attachments and request in this
conversation.
Subject: [describe the object].
Format and quantity: [for example, one 16:9 landscape image].
Preserve: [shape, color, structure, or an existing layout].
Show: [design drawings, transmitted light, soft paper layers, tools, or
other details].
Generate the image and continue refining it with my feedback.
```

You can also share the repository homepage and ask the model to open this guide. The link supplies creative context for the current conversation. Share the guide again when you need it in another conversation.

<a id="链接读取与图片生成"></a>

### Reading links and generating images

If the link cannot be read, paste this guide in full or upload the downloaded document, then send your request. If the conversation only supports text, ask for a complete prompt to use with your chosen image tool. To create the image directly, use a conversation with image generation available. See the [ChatGPT image guide](https://learn.chatgpt.com/docs/image-generation).

<a id="对话中的工作方式"></a>

## Working in the conversation

Read the user's request and the currently accessible materials first. Inspect each available attachment, and clearly identify any necessary image or document that cannot be viewed. This guide uses natural-language creative directions. When file access and Python are available and the user wants structured records, the [direction compilation workflow (Chinese)](references/prompt-execution.md) can also be used. Describe only steps that were actually performed.

When the user requests image generation or editing and an image tool is available, invoke it and obtain an image. In a text-only environment, deliver a copyable prompt and the intended attachment order. If the user requests only a prompt or analysis, deliver that requested content.

Available capabilities depend on the plan, platform, and workspace settings. Regular Chat follows ChatGPT's current messaging and image limits. ChatGPT Work and Codex share usage limits; see the [official usage guide](https://learn.chatgpt.com/docs/pricing).

<a id="创作流程"></a>

## Creative workflow

<a id="1-明确主体与保留项"></a>

### 1. Define the subject and what to preserve

Identify the object's real-world category, parts, and connections. Establish the silhouette, thickness, openings, joints, accessories, and support before describing the finish. Product photographs establish a specific object's shape. Style references establish the lighting, color, or arrangement to use. For a written brief, develop a concrete object from the user's description.

When editing, specify which objects, positions, proportions, colors, and paper edges must remain. For example, a long necklace with a small pendant should retain its length, slender chain, connecting rings, and pendant-to-chain proportions.

<a id="2-组织整幅画面"></a>

### 2. Organize the complete image

The default is a still life with transmitted light from below: a perpendicular top-down view of a bright, milky, slightly cool luminous table. The camera's optical axis is perpendicular to the surface, and the same continuous tabletop reaches all image edges. Establish the subject as the first point of attention, then arrange matching drawings, material samples, and useful tools into a clear viewing order. Follow the user's explicit choice of another style or a previously approved appearance.

Each drawing should correspond to a visible feature of the subject, such as its contour, structure, ornament, or material. Use spacing, orientation, grouping, and negative space to support the composition. Compose landscape and portrait images separately. The user's requested format and quantity take priority.

Keep the subject, required tools, and complete paper sheets inside the frame, with space around them. Use physically complete rectangular or square sheets with four right-angle corners and parallel opposite edges. When aligned upright, their top and bottom edges are horizontal. Frame close-ups around the detail selected by the user.

<a id="3-明确底光和纸层"></a>

### 3. Establish transmitted light and paper layers

The main light comes from below the milky diffusing surface, passing upward through thin paper or translucent material. A single sheet has its own density; overlaps are darker, and lower pencil lines become paler where an upper sheet covers them. Paper boundaries, single layers, overlaps, and covered drawing lines together make transmission visible. Requests for a lightbox, tracing paper, or translucent paper alone use these default lighting relationships. An explicit request for the soft paper archive style calls for subtler, softer tonal separation.

Opaque objects such as metal retain dark tones, reflections, and credible contact with the table. Lighting, shadows, occlusion, and material thickness belong to the same physical scene. Soft lighting must still reveal surfaces and layers clearly.

<a id="4-建立可信的细节"></a>

### 4. Build credible details

Check each object's form and connections against its actual function. Round-nose pliers have two tapered jaws, a connecting pivot, and two handles. Tweezers have connected arms and matching tips. A chain consists of continuously interlinked components.

Metal appearance follows its material and finish: gold has warm reflections, steel tools have silver-gray dark surfaces and narrow highlights, and fine engraving or brushing has a clear direction. Paper retains appropriate fibers and thin edges. Every object has plausible thickness, scale, support, and contact shadows.

<a id="5-整理提示词并成像"></a>

### 5. Assemble the prompt and generate

Combine the chosen direction into one complete prompt covering:

- Format, quantity, target dimensions, and intended use.
- Subject structure, materials, details, relative scale, and preservation requirements.
- Placement of the subject, drawings, paper layers, samples, and tools.
- Viewpoint, light from below, reflections, paper transmission, and contact shadows.
- The most important details to inspect and the required complete framing.

For an edit, identify the current image as the specific target. Assign a clear purpose to each attachment and state their order in the delivered prompt. If the user is refining details, preserve the established composition and subject proportions.

Any visible text must serve the user's request or the current artwork and appear on a defined paper, package, or physical surface.

<a id="6-检查与交付"></a>

### 6. Inspect and deliver

When the generated image can be viewed, check the complete composition, subject identity, object boundaries, paper layers, and lighting first. Then inspect chain links, tool tips, pivots, textures, edges, and contact at a larger scale. Correct specific issues within the authorized scope. Distinguish the generated result, visual assessment, and the user's selection.

Deliver the images or prompts requested. Report dimensions from the actual file. For an upscale, state the resulting dimensions and the method used. If generation, viewing, or reading dimensions is unavailable, identify the unfinished step accurately.

<a id="常用指令"></a>

## Copyable requests

<a id="生成一张光台静物图"></a>

### Generate a light-table still life

```text
Use the Siuyu Lightbox Still Life conversation workflow to create a 16:9
still life from my attachments.
Preserve the subject's real structure and materials. Arrange matching design
drawings on complete rectangular tracing paper.
Use a perpendicular top-down view and a milky tabletop filling the frame,
with light passing upward through the paper.
Make overlaps darker and lower sketch lines paler where they are covered.
Keep natural spacing and the subject and all paper edges fully in frame.
Generate one complete image.
```

<a id="为已有图片整理放大指令"></a>

### Prepare an upscaling prompt for an existing image

```text
Write a faithful upscaling prompt for this image.
Preserve the composition, object count, positions, proportions, all four
paper edges, and transmitted-light relationships.
Describe how to retain clear product textures, tool construction, metallic
reflections, and contact shadows.
The target size is [pixel dimensions]. Deliver one complete copyable prompt.
```

<a id="进一步阅读"></a>

## Further guidance

These detailed documents are maintained in Chinese. Read the ones relevant to the current task:

- [Image art direction](references/image-art-direction.md): hierarchy, grouping, visual weight, and negative space.
- [Physical realism](references/physical-realism.md): structure, scale, connections, and materials.
- [Paper layers and transmission](references/diffused-paper-archive.md): light from below, thin paper, overlaps, and drawings.
- [Framing and focus](references/camera-framing.md): aspect ratio, focus, and essential details.
- [Complete skill workflow](SKILL.md): saving files and running scripts when the required tools are available.

For platform capabilities, see OpenAI's guides to [using ChatGPT](https://learn.chatgpt.com/docs/use-chatgpt), [image generation](https://learn.chatgpt.com/docs/image-generation), and [web search](https://learn.chatgpt.com/docs/web-search).

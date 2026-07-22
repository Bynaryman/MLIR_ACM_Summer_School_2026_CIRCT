-- Group each regular slide's content separately from its heading.

local function is_nested_slide_group(block)
  if block.t ~= "Div" then
    return false
  end

  for _, child in ipairs(block.content) do
    if child.t == "Header" and child.level <= 2 then
      return true
    end
    if child.t == "Div" and is_nested_slide_group(child) then
      return true
    end
  end

  return false
end

local function group_slide_bodies(input_blocks)
  local output_blocks = {}
  local index = 1

  while index <= #input_blocks do
    local block = input_blocks[index]

    if is_nested_slide_group(block) then
      block.content = group_slide_bodies(block.content)
      table.insert(output_blocks, block)
      index = index + 1
    elseif block.t == "Header" and block.level == 2 then
      table.insert(output_blocks, block)
      index = index + 1

      local body = {}
      while index <= #input_blocks do
        local candidate = input_blocks[index]
        if (candidate.t == "Header" and candidate.level <= 2) or
            is_nested_slide_group(candidate) then
          break
        end

        table.insert(body, candidate)
        index = index + 1
      end

      if #body > 0 then
        table.insert(
          output_blocks,
          pandoc.Div(body, pandoc.Attr("", { "slide-body" }))
        )
      end
    else
      table.insert(output_blocks, block)
      index = index + 1
    end
  end

  return output_blocks
end

function Pandoc(document)
  if not FORMAT:match("revealjs") then
    return document
  end

  document.blocks = group_slide_bodies(document.blocks)
  return document
end

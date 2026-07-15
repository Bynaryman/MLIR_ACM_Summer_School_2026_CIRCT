-- Group each regular slide's content separately from its heading.
function Pandoc(document)
  if not FORMAT:match("revealjs") then
    return document
  end

  local blocks = {}
  local index = 1

  while index <= #document.blocks do
    local block = document.blocks[index]

    if block.t == "Header" and block.level == 2 then
      table.insert(blocks, block)
      index = index + 1

      local body = {}
      while index <= #document.blocks do
        local candidate = document.blocks[index]
        if candidate.t == "Header" and candidate.level <= 2 then
          break
        end

        table.insert(body, candidate)
        index = index + 1
      end

      if #body > 0 then
        table.insert(blocks, pandoc.Div(body, pandoc.Attr("", { "slide-body" })))
      end
    else
      table.insert(blocks, block)
      index = index + 1
    end
  end

  document.blocks = blocks
  return document
end

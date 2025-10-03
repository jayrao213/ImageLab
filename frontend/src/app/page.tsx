'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'

type Action =
  | 'add_color'
  | 'red_shift'
  | 'green_shift'
  | 'blue_shift'
  | 'shift_brightness'
  | 'make_monochrome'
  | 'mirror_horizontal'
  | 'mirror_vertical'
  | 'tile'
  | 'blur'
  | 'negative'
  | 'sepia'
  | 'rotate'
  | 'pixelate'
  | 'resize'
  | 'ai_generate'

type DownloadFormat = 'png' | 'jpg' | 'webp' | 'bmp'

export default function Page() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isBusy, setIsBusy] = useState(false)
  const [action, setAction] = useState<Action>('ai_generate')
  const [r, setR] = useState<string>('')
  const [g, setG] = useState<string>('')
  const [b, setB] = useState<string>('')
  const [amount, setAmount] = useState<string>('')
  const [factor, setFactor] = useState<string>('')
  const [size, setSize] = useState<string>('')
  const [degrees, setDegrees] = useState<string>('')
  const [block, setBlock] = useState<string>('')
  const [prompt, setPrompt] = useState<string>('')
  const [resizeWidth, setResizeWidth] = useState<string>('')
  const [resizeHeight, setResizeHeight] = useState<string>('')
  const [downloadFormat, setDownloadFormat] = useState<DownloadFormat>('png')
  const [hasModifications, setHasModifications] = useState(false)
  const currentBlob = useRef<Blob | null>(null)
  const originalBlob = useRef<Blob | null>(null)
  const currentObjectUrl = useRef<string | null>(null)

  const revoke = useCallback(() => {
    if (currentObjectUrl.current) URL.revokeObjectURL(currentObjectUrl.current)
    currentObjectUrl.current = null
  }, [])

  const onPick = useCallback(
    (f: File) => {
      setFile(f)
      currentBlob.current = f
      originalBlob.current = f
      setHasModifications(false)
      revoke()
      setPreviewUrl(null)
    },
    [revoke]
  )

  const controls = useMemo(() => {
    const labelCls = 'text-sm font-medium text-gray-700'
    const inputCls =
      'mt-1 block w-full rounded-md border border-gray-700 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
    return (
      <>
        {action === 'add_color' && (
          <div className="grid grid-cols-3 gap-3">
            <label className="flex flex-col">
              <span className={labelCls}>R</span>
              <input type="number" className={inputCls} value={r} placeholder="0" onChange={(e) => setR(e.target.value)} />
            </label>
            <label className="flex flex-col">
              <span className={labelCls}>G</span>
              <input type="number" className={inputCls} value={g} placeholder="0" onChange={(e) => setG(e.target.value)} />
            </label>
            <label className="flex flex-col">
              <span className={labelCls}>B</span>
              <input type="number" className={inputCls} value={b} placeholder="0" onChange={(e) => setB(e.target.value)} />
            </label>
          </div>
        )}
        {(action === 'red_shift' || action === 'green_shift' || action === 'blue_shift') && (
          <label className="flex flex-col">
            <span className={labelCls}>Amount</span>
            <input type="number" className={inputCls} value={amount} placeholder="0" onChange={(e) => setAmount(e.target.value)} />
          </label>
        )}
        {action === 'shift_brightness' && (
          <label className="flex flex-col">
            <span className={labelCls}>Factor</span>
            <input type="number" step="0.1" className={inputCls} value={factor} placeholder="1" onChange={(e) => setFactor(e.target.value)} />
          </label>
        )}
        {action === 'tile' && (
          <label className="flex flex-col">
            <span className={labelCls}>Size</span>
            <input type="number" min={1} className={inputCls} value={size} placeholder="2" onChange={(e) => setSize(e.target.value)} />
          </label>
        )}
        {action === 'rotate' && (
          <label className="flex flex-col">
            <span className={labelCls}>Degrees</span>
            <input type="number" className={inputCls} value={degrees} placeholder="90" onChange={(e) => setDegrees(e.target.value)} />
          </label>
        )}
        {action === 'pixelate' && (
          <label className="flex flex-col">
            <span className={labelCls}>Block size</span>
            <input type="number" className={inputCls} value={block} placeholder="8" onChange={(e) => setBlock(e.target.value)} />
          </label>
        )}
        {action === 'resize' && (
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col">
              <span className={labelCls}>Width</span>
              <input type="number" className={inputCls} value={resizeWidth} placeholder="800" onChange={(e) => setResizeWidth(e.target.value)} />
            </label>
            <label className="flex flex-col">
              <span className={labelCls}>Height</span>
              <input type="number" className={inputCls} value={resizeHeight} placeholder="600" onChange={(e) => setResizeHeight(e.target.value)} />
            </label>
          </div>
        )}
        {action === 'ai_generate' && (
          <label className="flex flex-col">
            <span className={labelCls}>Prompt</span>
            <input
              type="text"
              className={inputCls}
              value={prompt}
              placeholder="Describe the image to generate..."
              onChange={(e) => setPrompt(e.target.value)}
            />
          </label>
        )}
      </>
    )
  }, [action, r, g, b, amount, factor, size, degrees, block, prompt, resizeWidth, resizeHeight])

  const num = (s: string, fallback: number) => {
    const n = Number(s)
    return Number.isFinite(n) ? n : fallback
  }

  const apply = useCallback(async () => {
    const src = currentBlob.current ?? file
    if (!src && action !== 'ai_generate') {
      return alert('Pick an image first')
    }
    const form = new FormData()
    if (src) {
      form.append('file', src, 'current.png')
    }
    form.append('action', action)
    if (action === 'add_color') {
      form.append('r', String(num(r, 0)))
      form.append('g', String(num(g, 0)))
      form.append('b', String(num(b, 0)))
    } else if (action === 'red_shift' || action === 'green_shift' || action === 'blue_shift') {
      form.append('amount', String(num(amount, 0)))
    } else if (action === 'shift_brightness') {
      form.append('factor', String(num(factor, 1)))
    } else if (action === 'tile') {
      form.append('size', String(Math.max(1, num(size, 2))))
    } else if (action === 'rotate') {
      const deg = num(degrees, 90)
      if (deg % 90 !== 0) {
        alert('Rotation only supports multiples of 90°')
        return
      }
      form.append('degrees', String(deg))
    } else if (action === 'pixelate') {
      form.append('block', String(num(block, 8)))
    } else if (action === 'resize') {
      const w = num(resizeWidth, 0)
      const h = num(resizeHeight, 0)
      if (w < 1 || h < 1) {
        alert('Please enter valid width and height (at least 1)')
        return
      }
      form.append('resize_width', String(w))
      form.append('resize_height', String(h))
    } else if (action === 'ai_generate') {
      if (!prompt.trim()) {
        alert('Please enter a prompt for AI generation')
        return
      }
      form.append('prompt', prompt.trim())
      form.append('width', '512')
      form.append('height', '512')
    }
    setIsBusy(true)
    try {
      const res = await fetch(`${API}/apply`, { method: 'POST', body: form })
      if (!res.ok) {
        const msg = await res.text().catch(() => '')
        alert(msg || `Server error (${res.status})`)
        return
      }
      const blob = await res.blob()
      currentBlob.current = blob
      if (action === 'ai_generate') {
        originalBlob.current = blob
        setHasModifications(false)
      } else {
        if (!originalBlob.current) {
          originalBlob.current = blob
        }
        setHasModifications(true)
      }
      revoke()
      const url = URL.createObjectURL(blob)
      currentObjectUrl.current = url
      setPreviewUrl(url)
    } catch {
      alert('Could not reach the image API. Is it running and CORS-enabled?')
    } finally {
      setIsBusy(false)
    }
  }, [file, action, r, g, b, amount, factor, size, degrees, block, prompt, resizeWidth, resizeHeight, revoke])

  const reset = useCallback(() => {
    if (originalBlob.current) {
      currentBlob.current = originalBlob.current
      setHasModifications(false)
      revoke()
      const url = URL.createObjectURL(originalBlob.current)
      currentObjectUrl.current = url
      setPreviewUrl(url)
    }
  }, [revoke])

  const download = useCallback(() => {
    const blob = currentBlob.current
    if (!blob) return
    const a = document.createElement('a')
    const url = URL.createObjectURL(blob)
    if (downloadFormat === 'png') {
      a.href = url
      a.download = 'edited.png'
      a.click()
      URL.revokeObjectURL(url)
      return
    }
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      if (ctx) ctx.drawImage(img, 0, 0)
      const mime = downloadFormat === 'jpg' ? 'image/jpeg' : `image/${downloadFormat}`
      a.href = canvas.toDataURL(mime)
      a.download = `edited.${downloadFormat}`
      a.click()
    }
    img.src = url
  }, [downloadFormat])

  useEffect(() => () => revoke(), [revoke])

  const sectionCls = 'grid gap-3'

  return (
    <main className="mx-auto max-w-5xl p-4 font-sans">
      <h1 className="mb-3 text-7xl font-semibold">ImageLab</h1>
      <section className={`${sectionCls} mb-4`}> 
        <div>
          <input
            type="file"
            accept="image/*"
            onClick={(e) => { (e.currentTarget as HTMLInputElement).value = '' }}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) onPick(f)
            }}
            className="inline-block w-auto cursor-default text-sm text-gray-700 file:mr-3 file:rounded-md file:border-0 file:bg-indigo-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white file:transition file:duration-200 file:ease-in-out file:cursor-pointer hover:file:bg-indigo-700"
          />
        </div>
        <div className="flex flex-col gap-3 md:flex-row md:items-start">
          <label className="flex flex-col md:w-1/2">
            <span className="text-sm font-medium text-gray-700">Action</span>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value as Action)}
              className="mt-1 block w-full cursor-pointer rounded-md border border-gray-700 bg-[#0a0a0a] px-3 py-2 text-sm text-white shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ai_generate">AI Generate</option>
              <option value="resize">Resize</option>
              <option value="add_color">Add Color</option>
              <option value="red_shift">Red Shift</option>
              <option value="green_shift">Green Shift</option>
              <option value="blue_shift">Blue Shift</option>
              <option value="shift_brightness">Shift Brightness</option>
              <option value="make_monochrome">Make Monochrome</option>
              <option value="mirror_horizontal">Mirror Horizontal</option>
              <option value="mirror_vertical">Mirror Vertical</option>
              <option value="tile">Tile</option>
              <option value="blur">Blur</option>
              <option value="negative">Negative</option>
              <option value="sepia">Sepia</option>
              <option value="rotate">Rotate</option>
              <option value="pixelate">Pixelate</option>
            </select>
          </label>
          <div className="flex flex-col gap-3 md:w-1/2">{controls}</div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={apply}
            disabled={isBusy || (action !== 'ai_generate' && !file && !currentBlob.current) || (action === 'ai_generate' && !prompt.trim())}
            className="inline-flex cursor-pointer items-center justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition enabled:hover:bg-indigo-700 disabled:cursor-default disabled:opacity-50"
          >
            {isBusy ? 'Applying…' : 'Apply'}
          </button>
          <button
            onClick={reset}
            disabled={!hasModifications || !originalBlob.current}
            className="inline-flex cursor-pointer items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-900 shadow-sm transition enabled:hover:bg-gray-200 disabled:cursor-default disabled:opacity-50"
          >
            Reset
          </button>
          <select
            value={downloadFormat}
            onChange={(e) => setDownloadFormat(e.target.value as DownloadFormat)}
            disabled={!currentBlob.current}
            className="inline-flex cursor-pointer items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-900 shadow-sm transition enabled:hover:bg-gray-200 disabled:cursor-default disabled:opacity-50"
          >
            <option value="png">PNG</option>
            <option value="jpg">JPG</option>
            <option value="webp">WEBP</option>
            <option value="bmp">BMP</option>
          </select>
          <button
            onClick={download}
            disabled={!currentBlob.current}
            className="inline-flex cursor-pointer items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-900 shadow-sm ring-1 transition enabled:hover:bg-gray-200 disabled:cursor-default disabled:opacity-50"
          >
            Download
          </button>
        </div>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Preview</h2>
        <div className="grid min-h-110 place-items-center rounded-lg border border-gray-700 p-3">
          {previewUrl ? (
            <img src={previewUrl} alt="Edited preview" className="h-auto max-w-full rounded-lg" />
          ) : file ? (
            <img
              src={URL.createObjectURL(file)}
              onLoad={(e: React.SyntheticEvent<HTMLImageElement>) => {
                URL.revokeObjectURL(e.currentTarget.src)
              }}
              alt="Original"
              className="h-auto max-w-full rounded-lg"
            />
          ) : (
            <p className="text-sm text-white">Pick an image to begin.</p>
          )}
        </div>
      </section>
    </main>
  )
}
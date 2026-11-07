import { useEffect, useLayoutEffect, useRef, useState, type ReactNode, type UIEvent } from 'react';

/** Reclaim reading space while keeping navigation a short upward scroll away. */
export function ReaderChrome({ sectionId, navigation, children }: { sectionId: string; navigation: ReactNode; children: ReactNode }) {
  const [hidden, setHidden] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const header = useRef<HTMLDivElement>(null);
  const scroll = useRef({ top: 0, travel: 0 });
  const userScrollUntil = useRef(0);

  useEffect(() => {
    setHidden(false);
    scroll.current = { top: 0, travel: 0 };
    userScrollUntil.current = 0;
  }, [sectionId]);

  useLayoutEffect(() => {
    const measure = () => root.current?.style.setProperty('--reader-header-height', `${header.current!.offsetHeight}px`);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(header.current!);
    return () => observer.disconnect();
  }, []);

  const onScroll = (event: UIEvent<HTMLDivElement>) => {
    const pane = event.target as HTMLElement;
    if (!pane.classList.contains('reading-column')) return;
    // Clamp elastic scrolling and ignore bottom clamping when the pane grows.
    const max = Math.max(0, pane.scrollHeight - pane.clientHeight);
    const top = Math.max(0, Math.min(pane.scrollTop, max));
    const delta = top - Math.min(scroll.current.top, max);
    const travel = Math.sign(delta) === Math.sign(scroll.current.travel) ? scroll.current.travel + delta : delta;
    scroll.current = { top, travel };
    if (top <= 24) setHidden(false);
    // Word selection and search links also scroll the text programmatically.
    // Only reading gestures should collapse the navigation.
    if (performance.now() > userScrollUntil.current) {
      scroll.current.travel = 0;
      return;
    }
    userScrollUntil.current = performance.now() + 1500; // Include touch momentum.
    if (top <= 24) return;
    else if (travel <= -12) setHidden(false);
    else if (top > 80 && max > header.current!.offsetHeight + 80 && travel >= 32
      && !header.current?.querySelector(':focus-visible, [aria-expanded="true"]')) setHidden(true);
  };

  const readingGesture = (target: EventTarget) => {
    if ((target as HTMLElement).closest('.reading-column')) userScrollUntil.current = performance.now() + 1500;
  };

  return <div ref={root} className="reader-page" onScrollCapture={onScroll}
    onWheelCapture={event => readingGesture(event.target)}
    onTouchMoveCapture={event => readingGesture(event.target)}
    onPointerDownCapture={event => {
      // Clicks cancel earlier momentum; a scrollbar drag starts fresh input.
      userScrollUntil.current = 0;
      if ((event.target as HTMLElement).classList.contains('reading-column')) readingGesture(event.target);
    }}
    onKeyDownCapture={event => {
      if (['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End'].includes(event.key)
        || (event.key === ' ' && (event.target as HTMLElement).classList.contains('reading-column'))) readingGesture(event.target);
    }}>
    <div ref={header} className={`reader-header ${hidden ? 'is-hidden' : ''}`} onFocusCapture={() => setHidden(false)}>
      {navigation}
    </div>
    {children}
  </div>;
}

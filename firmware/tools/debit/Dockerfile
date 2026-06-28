FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    gcc \
    make \
    autoconf \
    automake \
    libtool \
    pkg-config \
    flex \
    bison \
    perl \
    libswitch-perl \
    xmlto \
    libglib2.0-dev \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone https://github.com/djn3m0/debit.git

WORKDIR /build/debit
# Use the repo's own bootstrap (autoreconf doesn't know about the ac_macros/ dir)
RUN aclocal -I ac_macros/ && autoconf && autoheader && automake --add-missing

# Disable asserts, debug output, and GTK+ GUI (headless container).
# Suppress warnings from old C on modern GCC with -w (no -Werror in the project, but playing safe).
RUN CFLAGS="-O2 -w" ./configure \
    --prefix=/usr/local \
    --enable-gtk=no \
    --disable-asserts \
    --disable-debug

# Replace SUBDIRS entirely — several subdirs can't build in a headless container:
#   xiledit — GUI, needs glade-2 + xvfb
#   xdl     — bison API compat broken with modern bison (yyparm ABI removed)
#   desktop — needs inkscape for SVG→PNG icon conversion
#   windows/debian/rpm — packaging scripts only
# We keep: data (chip databases), doc, altera, utils, codes, tests
RUN sed -i 's/^SUBDIRS = .*/SUBDIRS = data doc altera utils codes tests/' Makefile

RUN make -j"$(nproc)"
RUN make install DESTDIR=/install


FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install/usr/local /usr/local

# Debit looks for chip data files relative to its install prefix at runtime
ENV DEBIT_DATADIR=/usr/local/share/debit

WORKDIR /work
ENTRYPOINT ["debit"]
CMD ["--help"]

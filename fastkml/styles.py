# Copyright (C) 2012 - 2023 Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Once you've created features within Google Earth and examined the KML
code Google Earth generates, you'll notice how styles are an important
part of how your data is displayed.
"""

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.base import _XMLObject
from fastkml.enums import ColorMode
from fastkml.enums import DisplayMode
from fastkml.enums import PairKey
from fastkml.enums import Units
from fastkml.enums import Verbosity
from fastkml.helpers import bool_subelement
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import subelement_bool_kwarg
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.helpers import xml_subelement_list
from fastkml.helpers import xml_subelement_list_kwarg
from fastkml.links import Icon
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.types import Element

logger = logging.getLogger(__name__)


class StyleUrl(_BaseObject):
    """
    URL of a <Style> or <StyleMap> defined in a Document.

    If the style is in the same file, use a # reference.
    If the style is defined in an external file,
    use a full URL along with # referencing.

    https://developers.google.com/kml/documentation/kmlreference#styleurl
    """

    url: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.url = url

    def __repr__(self) -> str:
        """Create a string (c)representation for StyleUrl."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"url={self.url!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.url)

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        element.text = self.url or ""
        return element

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return "styleUrl"

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["url"] = element.text
        return kwargs


class _StyleSelector(_BaseObject):
    """
    This is an abstract element and cannot be used directly in a KML file.
    It is the base type for the <Style> and <StyleMap> elements. The
    StyleMap element selects a style based on the current mode of the
    Placemark. An element derived from StyleSelector is uniquely identified
    by its id and its url.

    https://developers.google.com/kml/documentation/kmlreference#styleselector
    """


class _ColorStyle(_BaseObject):
    """
    abstract element; do not create.
    This is an abstract element and cannot be used directly in a KML file.
    It provides elements for specifying the color and color mode of
    extended style types.
    subclasses are: IconStyle, LabelStyle, LineStyle, PolyStyle.
    https://developers.google.com/kml/documentation/kmlreference#colorstyle
    """

    id = None
    color = None
    # Color and opacity (alpha) values are expressed in hexadecimal notation.
    # The range of values for any one color is 0 to 255 (00 to ff).
    # For alpha, 00 is fully transparent and ff is fully opaque.
    # The order of expression is aabbggrr, where aa=alpha (00 to ff);
    # bb=blue (00 to ff); gg=green (00 to ff); rr=red (00 to ff).

    color_mode: Optional[ColorMode]
    # Values for <colorMode> are normal (no effect) and random.
    # A value of random applies a random linear scale to the base <color>

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[ColorMode] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.color = color
        self.color_mode = color_mode

    def __repr__(self) -> str:
        """Create a string (c)representation for _ColorStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"color={self.color!r}, "
            f"color_mode={self.color_mode!r}, "
            ")"
        )


registry.register(
    _ColorStyle,
    RegistryItem(
        attr_name="color",
        node_name="color",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _ColorStyle,
    RegistryItem(
        attr_name="color_mode",
        node_name="colorMode",
        classes=(ColorMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


class HotSpot(_XMLObject):
    """
    Specifies the position within the Icon that is "anchored" to the <Point>.

    x - Either the number of pixels, a fractional component of the icon,
    or a pixel inset indicating the x component of a point on the icon.
    y - Either the number of pixels, a fractional component of the icon,
    or a pixel inset indicating the y component of a point on the icon.
    xunits - Units in which the x value is specified.
    A value of fraction indicates the x value is a fraction of the icon.
    A value of pixels indicates the x value in pixels.
    A value of insetPixels indicates the indent from the right edge of the icon.
    yunits - Units in which the y value is specified.

    https://developers.google.com/kml/documentation/kmlreference#hotspot
    """

    x: Optional[float]
    y: Optional[float]
    xunits: Optional[Units]
    yunits: Optional[Units]

    _default_ns = config.KMLNS

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        xunits: Optional[Units] = None,
        yunits: Optional[Units] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.x = x
        self.y = y
        self.xunits = xunits
        self.yunits = yunits

    def __repr__(self) -> str:
        """Create a string (c)representation for HotSpot."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"x={self.x!r}, "
            f"y={self.y!r}, "
            f"xunits={self.xunits!r}, "
            f"yunits={self.yunits!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return all((self.x is not None, self.y is not None))

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        hot_spot = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}hotSpot",
        )
        hot_spot.attrib["x"] = str(self.x)
        hot_spot.attrib["y"] = str(self.y)
        if self.xunits:
            hot_spot.attrib["xunits"] = self.xunits.value
        if self.yunits:
            hot_spot.attrib["yunits"] = self.yunits.value
        return element

    @classmethod
    def get_tag_name(cls) -> str:
        """Return the tag name."""
        return "hotSpot"

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        kwargs["x"] = float(element.get("x"))
        kwargs["y"] = float(element.get("y"))
        if element.get("xunits"):
            kwargs["xunits"] = Units(element.get("xunits"))
        if element.get("yunits"):
            kwargs["yunits"] = Units(element.get("yunits"))
        return kwargs


class IconStyle(_ColorStyle):
    """
    Specifies how icons for point Placemarks are drawn.

    The <Icon> element specifies the icon image.
    The <scale> element specifies the x, y scaling of the icon.
    The color specified in the <color> element of <IconStyle> is blended with the
    color of the <Icon>.

    https://developers.google.com/kml/documentation/kmlreference#iconstyle
    """

    scale: Optional[float]
    # Resizes the icon. (float)
    heading: Optional[float]
    # Direction (that is, North, South, East, West), in degrees.
    # Default=0 (North).
    icon_href: Optional[str]
    # An HTTP address or a local file specification used to load an icon.
    hot_spot: Optional[HotSpot]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[ColorMode] = None,
        scale: Optional[float] = None,
        heading: Optional[float] = None,
        icon: Optional[Icon] = None,
        hot_spot: Optional[HotSpot] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
        )

        self.scale = scale
        self.heading = heading
        self.icon = icon
        self.hot_spot = hot_spot

    def __repr__(self) -> str:
        """Create a string (c)representation for IconStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"color={self.color!r}, "
            f"color_mode={self.color_mode!r}, "
            f"scale={self.scale!r}, "
            f"heading={self.heading!r}, "
            f"icon={self.icon!r}, "
            f"hot_spot={self.hot_spot!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.icon)


registry.register(
    IconStyle,
    RegistryItem(
        attr_name="scale",
        node_name="scale",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    IconStyle,
    RegistryItem(
        attr_name="heading",
        node_name="heading",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    IconStyle,
    RegistryItem(
        attr_name="icon",
        node_name="Icon",
        classes=(Icon,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    IconStyle,
    RegistryItem(
        attr_name="hot_spot",
        node_name="hotSpot",
        classes=(HotSpot,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class LineStyle(_ColorStyle):
    """
    The drawing style (color, color mode, and line width) for all line geometry.

    Line geometry includes the outlines of outlined polygons and the extruded "tether"
    of Placemark icons (if extrusion is enabled).
    https://developers.google.com/kml/documentation/kmlreference#linestyle
    """

    width: Optional[float]
    # Width of the line, in pixels.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[ColorMode] = None,
        width: Optional[float] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
        )
        self.width = width

    def __repr__(self) -> str:
        """Create a string (c)representation for LineStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"color={self.color!r}, "
            f"color_mode={self.color_mode!r}, "
            f"width={self.width!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return self.width is not None


registry.register(
    LineStyle,
    RegistryItem(
        attr_name="width",
        node_name="width",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class PolyStyle(_ColorStyle):
    """
    Drawing style for polygons.

    Specifies the drawing style for all polygons, including polygon
    extrusions (which look like the walls of buildings) and line
    extrusions (which look like solid fences).

    https://developers.google.com/kml/documentation/kmlreference#polystyle
    """

    fill: Optional[bool]
    # Boolean value. Specifies whether to fill the polygon.
    outline: Optional[bool]
    # Boolean value. Specifies whether to outline the polygon.
    # Polygon outlines use the current LineStyle.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[ColorMode] = None,
        fill: Optional[bool] = None,
        outline: Optional[bool] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
        )
        self.fill = fill
        self.outline = outline

    def __repr__(self) -> str:
        """Create a string (c)representation for PolyStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"color={self.color!r}, "
            f"color_mode={self.color_mode!r}, "
            f"fill={self.fill!r}, "
            f"outline={self.outline!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return self.fill is not None or self.outline is not None


registry.register(
    PolyStyle,
    RegistryItem(
        attr_name="fill",
        node_name="fill",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)
registry.register(
    PolyStyle,
    RegistryItem(
        attr_name="outline",
        node_name="outline",
        classes=(bool,),
        get_kwarg=subelement_bool_kwarg,
        set_element=bool_subelement,
    ),
)


class LabelStyle(_ColorStyle):
    """
    Specifies how the <name> of a Feature is drawn in the 3D viewer.

    A custom color, color mode, and scale for the label (name) can be specified.

    https://developers.google.com/kml/documentation/kmlreference#labelstyle
    """

    scale: Optional[float]
    # Resizes the label.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        color: Optional[str] = None,
        color_mode: Optional[ColorMode] = None,
        scale: Optional[float] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            color=color,
            color_mode=color_mode,
        )
        self.scale = scale

    def __repr__(self) -> str:
        """Create a string (c)representation for LabelStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"color={self.color!r}, "
            f"color_mode={self.color_mode!r}, "
            f"scale={self.scale!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return any(
            (
                self.scale is not None,
                self.color is not None,
                self.color_mode is not None,
            ),
        )


registry.register(
    LabelStyle,
    RegistryItem(
        attr_name="scale",
        node_name="scale",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class BalloonStyle(_BaseObject):
    """
    Specifies how the description balloon for placemarks is drawn.

    The <bgColor>, if specified, is used as the background color of the balloon.

    https://developers.google.com/kml/documentation/kmlreference#balloonstyle
    """

    bg_color: Optional[str]
    # Background color of the balloon (optional). Color and opacity (alpha)
    # values are expressed in hexadecimal notation. The range of values for
    # any one color is 0 to 255 (00 to ff). The order of expression is
    # aabbggrr, where aa=alpha (00 to ff); bb=blue (00 to ff);
    # gg=green (00 to ff); rr=red (00 to ff).
    # For alpha, 00 is fully transparent and ff is fully opaque.
    # For example, if you want to apply a blue color with 50 percent
    # opacity to an overlay, you would specify the following:
    # <bgColor>7fff0000</bgColor>, where alpha=0x7f, blue=0xff, green=0x00,
    # and red=0x00. The default is opaque white (ffffffff).
    # Note: The use of the <color> element within <BalloonStyle> has been
    # deprecated. Use <bgColor> instead.

    text_color: Optional[str]
    # Foreground color for text. The default is black (ff000000).

    text: Optional[str]
    # Text displayed in the balloon. If no text is specified, Google Earth
    # draws the default balloon (with the Feature <name> in boldface,
    # the Feature <description>, links for driving directions, a white
    # background, and a tail that is attached to the point coordinates of
    # the Feature, if specified).
    # You can add entities to the <text> tag using the following format to
    # refer to a child element of Feature: $[name], $[description], $[address],
    # $[id], $[Snippet]. Google Earth looks in the current Feature for the
    # corresponding string entity and substitutes that information in the
    # balloon.
    # To include To here - From here driving directions in the balloon,
    # use the $[geDirections] tag. To prevent the driving directions links
    # from appearing in a balloon, include the <text> element with some content
    # or with $[description] to substitute the basic Feature <description>.
    # For example, in the following KML excerpt, $[name] and $[description]
    # fields will be replaced by the <name> and <description> fields found
    # in the Feature elements that use this BalloonStyle:
    # <text>This is $[name], whose description is:<br/>$[description]</text>

    display_mode: Optional[DisplayMode]
    # If <displayMode> is default, Google Earth uses the information supplied
    # in <text> to create a balloon . If <displayMode> is hide, Google Earth
    # does not display the balloon. In Google Earth, clicking the List View
    # icon for a Placemark whose balloon's <displayMode> is hide causes
    # Google Earth to fly to the Placemark.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        text: Optional[str] = None,
        display_mode: Optional[DisplayMode] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.bg_color = bg_color
        self.text_color = text_color
        self.text = text
        self.display_mode = display_mode

    def __repr__(self) -> str:
        """Create a string (c)representation for BalloonStyle."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"bg_color={self.bg_color!r}, "
            f"text_color={self.text_color!r}, "
            f"text={self.text!r}, "
            f"display_mode={self.display_mode!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return any(
            (
                self.bg_color is not None,
                self.text_color is not None,
                self.text is not None,
                self.display_mode is not None,
            ),
        )


registry.register(
    BalloonStyle,
    RegistryItem(
        attr_name="bg_color",
        node_name="bgColor",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    BalloonStyle,
    RegistryItem(
        attr_name="text_color",
        node_name="textColor",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    BalloonStyle,
    RegistryItem(
        attr_name="text",
        node_name="text",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    BalloonStyle,
    RegistryItem(
        attr_name="display_mode",
        node_name="displayMode",
        classes=(DisplayMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


AnyStyle = Union[BalloonStyle, IconStyle, LabelStyle, LineStyle, PolyStyle]


class Style(_StyleSelector):
    """
    A Style defines an addressable style group.

    It can be referenced by StyleMaps and Features.
    Styles affect how Geometry is presented in the 3D viewer and how Features
    appear in the Places panel of the List view.
    Shared styles are collected in a <Document> and must have an id defined for them
    so that they can be referenced by the individual Features that use them.

    https://developers.google.com/kml/documentation/kmlreference#style
    """

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        styles: Optional[Iterable[AnyStyle]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.styles = list(styles) if styles else []

    def __repr__(self) -> str:
        """Create a string (c)representation for Style."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"styles={self.styles!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return any(self.styles)


registry.register(
    Style,
    RegistryItem(
        attr_name="styles",
        node_name="Style",
        classes=(
            BalloonStyle,
            IconStyle,
            LabelStyle,
            LineStyle,
            PolyStyle,
        ),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


class Pair(_BaseObject):
    """
    Stylemap pair.

    Defines a key/value pair that maps a mode (normal or highlight) to the predefined
    <styleUrl>.
    <Pair> contains two elements (both are required):
        <key>, which identifies the key
        <styleUrl> or <Style>, which references the style.
        In <styleUrl>, for referenced style elements that are local to the KML document,
        a simple # referencing is used.
        For styles that are contained in external files, use a full URL along with
        # referencing.

    https://developers.google.com/kml/documentation/kmlreference#stylemap
    """

    key: Optional[PairKey]
    style: Optional[Union[StyleUrl, Style]]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        key: Optional[PairKey] = None,
        style: Optional[Union[StyleUrl, Style]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.key = key
        self.style = style

    def __repr__(self) -> str:
        """Create a string (c)representation for Pair."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"key={self.key!r}, "
            f"style={self.style!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return all((self.key is not None, self.style is not None))


registry.register(
    Pair,
    RegistryItem(
        attr_name="key",
        node_name="key",
        classes=(PairKey,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)
registry.register(
    Pair,
    RegistryItem(
        attr_name="style",
        node_name="style",
        classes=(
            StyleUrl,
            Style,
        ),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class StyleMap(_StyleSelector):
    """
    A <StyleMap> maps between two different Styles.
    Typically a <StyleMap> element is used to provide separate normal and highlighted
    styles for a placemark, so that the highlighted version appears when
    the user mouses over the icon in Google Earth.

    https://developers.google.com/kml/documentation/kmlreference#stylemap
    """

    pairs: List[Pair]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        pairs: Optional[Iterable[Pair]] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self.pairs = list(pairs) if pairs else []

    def __repr__(self) -> str:
        """Create a string (c)representation for StyleMap."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"pairs={self.pairs!r}, "
            ")"
        )

    def __bool__(self) -> bool:
        return bool(self.pairs)

    @property
    def normal(self) -> Optional[Union[StyleUrl, Style]]:
        return next(
            (pair.style for pair in self.pairs if pair.key == PairKey.normal),
            None,
        )

    @property
    def highlight(self) -> Optional[Union[StyleUrl, Style]]:
        return next(
            (pair.style for pair in self.pairs if pair.key == PairKey.highlight),
            None,
        )


registry.register(
    StyleMap,
    RegistryItem(
        attr_name="pairs",
        node_name="Pair",
        classes=(Pair,),
        get_kwarg=xml_subelement_list_kwarg,
        set_element=xml_subelement_list,
    ),
)


__all__ = [
    "BalloonStyle",
    "IconStyle",
    "LabelStyle",
    "LineStyle",
    "PolyStyle",
    "Style",
    "StyleMap",
    "StyleUrl",
]
